This is a project I created for Data Programming at App State. It performs a DFS search of the website Bitchute,
which is a website known for hosting hateful, extremist content, and stores the comments of all the videos it finds.
The website appears to be written in a dynamic Javascript framework, so I had to experiment to get data in a useable format.
*I also would not recommend looking too closely at the data being scraped if you have any sensitivities at all that may
be offended.*

```
python -m pip install -r requirements.txt
python -m scrapy crawl chute
```

Note that in the future this scraper may not work due to the usual host of reasons that scrapers are brittle (frontend design changes, changes to robots.txt, etc). While I am interested in extremism, I don't have time to maintain this code indefinitely.
