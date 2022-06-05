#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import numpy as np 
import pandas as pd 
from queue import Queue 
from rich import print
import time
import pickle
import os
import yaml 
import glob

DATA_PATH='../data/raw'

def is_movie(link):
    if link:
        return 'title.rme' in link 
    else:
        return False

def is_actor(link):
    if link:
        return 'person.rme' in link 
    else:
        return False

def is_iafd_link(link):
    if link:
        return 'www.iafd.com' in link 
    else:
        return False

def check_iafd_base(link):
    if link.startswith('/'):
        link = 'https://www.iafd.com' + link
    return link 

def replace_with_https(link):
    if link.startswith('http://'):
        link = link.replace('http', 'https')
    return link

def valid_link(link):
    link = replace_with_https(link)
    link = check_iafd_base(link)
    return link

def get_href(s):
    link = None
    if s.find('a'):
        link = valid_link(s.a['href'])
    return link

def parse_title(soup):
    return soup.find('h1').get_text().strip()
        
def parse_bio(soup):
    bio_query = soup.select('[class^=bio]')
    bio_data = dict()
    
    i, k = 0, None
    while i < len(bio_query):
        q = bio_query[i]
        c = q['class']
        t = q.get_text().strip()
        if 'bioheading' in c:
            k = t.replace('\n','')
        elif 'biodata' in c:
            if k not in bio_data:
                bio_data[k] = []
            if 'no data' in t.lower():
                t = 'None'
            bio_data[k].append(t)
        i += 1
    return bio_data

def parse_table_row(row):
    row_data = []
    if row.find('th'):        
        for th in row.find_all('th'):
            t = th.get_text().strip()
            row_data.extend([t, 'LINK[%s]' %(t)])

    elif row.find('td'):
        for td in row.find_all('td'):
            row_data.extend([td.get_text().strip(), get_href(td)])
    return row_data

def parse_movie_table_of_actor(soup):
    tbl = soup.find('table',{'class':'table'})
    movie_data = [parse_table_row(row) for row in tbl.find_all('tr')]
    movie_data = pd.DataFrame(movie_data[1:], columns=movie_data[0])

    movie_links = movie_data['LINK[Movie Title]'].to_list()
    movie_links = [link for link in movie_links if is_movie(link)]

    return movie_data, movie_links

def parse_actor_in_movie(person):
    txt, role = list(person.stripped_strings), ''
    actor = txt[0]
    if len(txt) > 1:
        role = ';'.join(txt[1:])
        
    link = get_href(person)
    
    return dict(
        Actor = actor,
        Role = role,
        Link = link        
    )

def parse_actor_list_in_movie(soup):
    actor_data = soup.find_all('div', {'class': 'castbox'})
    actor_data = [parse_actor_in_movie(x) for x in actor_data]
    
    actor_links = [actor['Link'] for actor in actor_data]
    actor_links = [link for link in actor_links if is_actor(link)]
    
    return pd.DataFrame(actor_data), actor_links

def parse_movie_details(soup):
    ignore_h3 = ['Performers', 'Buy This Movie', 'External Reviews', 'Usage Notice']
    movie_details = {}
    for h3t in soup.find_all('h3'):
        h3t_text = h3t.get_text().strip()
        if h3t_text in ignore_h3:
            continue 
        all_lis = h3t.parent.nextSibling.find_all('li')
        movie_details[h3t_text] = [li.text.strip() for li in all_lis] 
    return movie_details


class IAFDCrawler:

    parsed_links = dict(
        actor = set(), 
        movie = set()
    )
    
    queued_links = dict(
        actor = Queue(), 
        movie = Queue()
    )
    
    chkpnt = dict(
        actor = 'tmp/chkpnt_actor.txt',
        movie = 'tmp/chkpnt_movie.txt'
    )

    actors = []
    movies = [] 
    
    list_of_headers = []
    headers = {}
    
    filter_out = {}

    t = 0
    
    def __init__(self, list_of_headers = [], 
                 hdr_change_freq = 5, 
                 pause_freq = 12,
                 pause_sec = 5, 
                 save_every = 100,
                 filter_file = None,
                 parsedlink_file = None,
                 stop_after = None):
        
        if len(list_of_headers) == 0:
            list_of_headers = [{
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
            }]

        self.list_of_headers = list_of_headers
        self.hdr_change_freq = hdr_change_freq
        self.pause_freq = pause_freq
        self.pause_sec = pause_sec
        self.stop_after = stop_after
        self.save_every = save_every
        
        self.random_headers()

        if parsedlink_file:
            with open(parsedlink_file, 'r') as f:
                p = yaml.safe_load(f)
            self.parsed_links = {k: set(v) for k, v in p.items()}
        
        self.filter_file = filter_file
        self.load_filters()

    def load_filters(self):
        file_name = self.filter_file

        if file_name is None:
            self.filter_out['enable'] = False
            return

        with open(file_name, 'r') as f:
            self.filter_out = yaml.safe_load(f)
        print('[green]INFO: Loaded filter file [italic]"%s"' %(file_name))
        print(self.filter_out)
    
    def reject(self, url):
        if not self.filter_out['enable']:
            return False
        
        def get_criteria(filter_dict):
            filter_key = list(filter_dict.keys())[0]
            filter_val = filter_dict[filter_key]
            if type(filter_val) is not list:
                filter_val = [filter_val]
            
            list_of_filters = [f'{filter_key}={x}' in url for x in filter_val]
            filter_result = any(list_of_filters)
            prob_reject = filter_dict['prob']

            if filter_result:
                return np.random.rand() < prob_reject
            else:
                return False
            
        if is_movie(url):
            return get_criteria(self.filter_out['movie'])
        
        if is_actor(url):
            return get_criteria(self.filter_out['actor'])

    def random_headers(self):
        num_hobj = len(self.list_of_headers)
        ind_hobj = np.random.choice(num_hobj) 
        self.headers = self.list_of_headers[ind_hobj]   
        
        usragnt = self.headers.get('User-Agent', '')
        print('[green]INFO: [bold]HEADERS SWITCH[/bold]', usragnt)
        
    def initialize_queue(self, actor=None, movie=None, load_from_chkpnt=False):
        if load_from_chkpnt:
            with open(self.chkpnt['actor'], 'r') as f:
                actor = f.read().split('\n')[:-1]
            with open(self.chkpnt['movie'], 'r') as f:
                movie = f.read().split('\n')[:-1]
            print('[green]INFO: Loaded from [bold]checkpoints[/bold]: [blue]%d actors[/blue] and [red]%d movies[/red]' %(len(actor), len(movie))) 

        if type(actor) is not list:
            actor = [actor]
        if type(movie) is not list: 
            movie = [movie]
        
        for a in set(actor):
            if a in self.parsed_links['actor'] or len(a) == 0: continue 
            self.queued_links['actor'].put(a)

        for m in set(movie):
            if m in self.parsed_links['movie'] or len(m) == 0: continue
            self.queued_links['movie'].put(m)
        
    def get_queue(self, role='actor'):
        already_parsed = True
        while already_parsed:            
            if self.queued_links[role].empty():
                print('[green]INFO: [bold]EMPTY %s QUEUE[/bold]' %(role))    
                return None
            link = self.queued_links[role].get()
            already_parsed = link in self.parsed_links[role]
        return link
    
    def run(self):        
        while True:
            actor_link = self.get_queue('actor')
            movie_link = self.get_queue('movie')

            self.request(actor_link)
            self.request(movie_link)

            if self.t == self.stop_after:
                break 
                
    def request(self, url):
        if url is None:
            return 
        
        if self.reject(url):
            return

        t0 = time.time()
        
        try:
            f = requests.get(url, headers = self.headers, timeout=10)
        except:
            print("[white on red]ERROR with [italic]%s[/italic]" %(url))
            return

        if f.status_code != 200:
            print("[white on yellow][%d] Issue with [italic]%s" %(self.t, url))
            return 
        
        soup = BeautifulSoup(f.content,'lxml')
        
        if is_actor(url):
            proc_fn = self.process_actor
        
        if is_movie(url):
            proc_fn = self.process_movie
        
        try:
            message = proc_fn(soup, url)
        except: 
            print("[white on red]ERROR with [italic]%s[/italic]" %(url))
            return

        t1 = time.time()
        
        print('[%d] %s ... [italic]elapsed %.2f seconds[/italic]' %(self.t,message,t1-t0))
        
        if self.t % self.save_every == 0 and self.t > 1:
            self.save() 
            
        if self.t % self.hdr_change_freq == 0 and self.t > 1:
            self.random_headers()

        if self.t % self.pause_freq == 0 and self.t > 1:
            print('[green]INFO: [bold]SLEEPING[/bold] (%.2f seconds)' %(self.pause_sec))     
            time.sleep(self.pause_sec)
            
        self.t += 1
    
    def save(self, file_dir = DATA_PATH):
        curr_time = '_' + time.strftime("%Y-%m-%d_%H-%M-%S_UTC", time.gmtime())
        actor_file = os.path.join(file_dir, 'actors' + curr_time + '.pkl')
        movie_file = os.path.join(file_dir, 'movies' + curr_time + '.pkl')
        parsed_file = os.path.join(file_dir, 'parsed-links' + curr_time + '.yaml')
        
        with open(actor_file,'wb') as f:
            pickle.dump(self.actors, f)

        with open(movie_file,'wb') as f:
            pickle.dump(self.movies, f)
            
        with open(parsed_file, 'w') as f:
            parsed_links = {k: list(v) for k, v in self.parsed_links.items()}
            yaml.safe_dump(parsed_links,f)
        
        with open(self.chkpnt['actor'], 'w') as f:
            f.write('')

        with open(self.chkpnt['movie'], 'w') as f:
            f.write('')

        print('[green]==> [bold]SAVED[/bold] [italic]%s, %s, %s[/italic]' %(actor_file, movie_file, parsed_file))

        self.actors = []
        self.movies = [] 
        
        self.load_filters()

    def process_actor(self, soup, url):
        movie_data, movie_links = parse_movie_table_of_actor(soup)
        
        actor_data = dict(
            NAME = parse_title(soup), 
            INFO = parse_bio(soup),
            MOVIES = movie_data,
            SOURCE = url
        )
        
        self.actors.append(actor_data)
        self.parsed_links['actor'].add(url)
        
        movie_links = [link for link in movie_links 
                       if link not in self.parsed_links['movie']]
        
        [self.queued_links['movie'].put(link) for link in movie_links]
        
        message = '''[bold][white on blue]ACTOR[/white on blue][/bold] [italic]%s[/italic] parsed, added [blue]%d movie links[/blue] to queue''' %(actor_data['NAME'], len(movie_links))
        
        with open(self.chkpnt['actor'], 'a') as f:
            f.write(url + '\n')

        return message 
    
    def process_movie(self, soup, url):
        actor_data, actor_links = parse_actor_list_in_movie(soup)
        
        movie_data = dict(
            NAME = parse_title(soup), 
            INFO = parse_bio(soup),
            ACTORS = actor_data,
            DETAILS = parse_movie_details(soup),
            SOURCE = url
        )
        
        self.movies.append(movie_data)
        self.parsed_links['movie'].add(url)
        
        actor_links = [link for link in actor_links 
                       if link not in self.parsed_links['actor']]
        
        [self.queued_links['actor'].put(link) for link in actor_links]
        
        message = '''[bold][white on red]MOVIE[/white on red][/bold] [italic]%s[/italic] parsed, added [red]%d actor links[/red] to queue''' %(movie_data['NAME'], len(actor_links))
        
        with open(self.chkpnt['movie'], 'a') as f:
            f.write(url + '\n')

        return message


list_of_usragents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
]

list_of_headers = [{'User-Agent': x} for x in list_of_usragents]

parsedlink_file = sorted(glob.glob(DATA_PATH + '/parsed*'))[-1]
filter_file = 'config/filters.yaml'

print('[green]INFO: Using previously parsed file [italic]"%s"' %(parsedlink_file))

crawler = IAFDCrawler(
    list_of_headers=list_of_headers,
    hdr_change_freq = 20, 
    pause_freq = 30,
    pause_sec = 2, 
    save_every = 500,
    parsedlink_file = parsedlink_file,
    filter_file = filter_file
)

crawler.initialize_queue(load_from_chkpnt=True)

crawler.run()

