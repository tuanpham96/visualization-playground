// this is to get movie title links from the website to serve as seeds
links = Array.from(document.getElementsByTagName('table')[0].getElementsByTagName('a'))
        .map(l => l.href)
        .filter(l => l.includes('title.rme'))
        .filter((x, i, a) => a.indexOf(x) == i)
        .join("<br>")

$('body').replaceWith('<body>' + links +'</body>');

