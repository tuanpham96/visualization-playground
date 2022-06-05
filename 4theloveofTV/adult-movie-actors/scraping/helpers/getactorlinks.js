// this is to get actor/performer links from the website to serve as seeds
links = Array.from(document.getElementsByTagName('table')[1].getElementsByTagName('a'))
        .map(l => l.href)
        .filter(l => l.includes('person.rme'))
        .filter((x, i, a) => a.indexOf(x) == i)
        .join("<br>")

$('body').replaceWith('<body>' + links +'</body>');

