# Notes on streaming platforms 

## General notes 

- For now only consider TV series
- Genres: scripted (drama, comedy, animation, family, miniseries) and unscripted (docuseries, reality) x (English, non-English)
- Include continuations but analyze separately; or maybe ignore entirely because would need to analyze ony the seasons that the shows were taken over to the new streaming platforms, plus this also means that the shows are not original of the given streaming platforms; however it might complicate things when analyze shows ended in one platform and continued in another (wondering if there are any indications in the tables) 
- Ignore co-productions (to make sure it is nearest to original) and exclusive international programming 
- Unclear what to do with podcasts, specials and regionals
- The layout of these Wikitables are quite similar to each other 
- For now combine HBO and HBO Max 
- For now separate Hulu and Disney+, though might need to include a separate analysis that combines them since Disney bought Hulu
- Same story for FX, ABC, though not considering traditionals 
- More traditional: ignore FX (FXNow), ignore ABC, ignore AMC, include HBO
- Unclear whether to include Upcoming to predict whether they would perform well based on the people involved (directors, actors, actress) and materials (titles, genres, texts) 

## Platform tables 

- Netflix:
  - [ongoing TV](https://wikiless.org/wiki/List_of_Netflix_original_programming#Co-productions): from section 1 to 5
  - [ended TV](https://wikiless.org/wiki/List_of_ended_Netflix_original_programming?lang=en)
  - ignore movies, stand-up comedies specials, exclusive international programming
- Apple TV:
  - [TV](https://wikiless.org/wiki/List_of_Apple_TV%2B_original_programming): only section 1
- HBO: combing HBO and HBO max
  - [HBO Max](https://wikiless.org/wiki/List_of_HBO_Max_original_programming?lang=en): only section 1, ignore 1.6, take note 1.7
  - [HBO](https://wikiless.org/wiki/List_of_HBO_original_programming?lang=en) ignore section 2
- Hulu:
  - [TV](https://wikiless.org/wiki/List_of_Hulu_original_programming?lang=en): ignore section 2
- Disney+:
  - [TV](https://wikiless.org/wiki/List_of_Disney%2B_original_programming?lang=en): uncear what to do with shorts
  - [Star](https://wikiless.org/wiki/List_of_Star_(Disney%2B)_original_programming?lang=en) since Star is a hub of Disney 
- Peacock:
  - [TV](https://wikiless.org/wiki/List_of_Peacock_original_programming?lang=en): ignore original films
- Paramount+:
  - [TV](https://wikiless.org/wiki/List_of_Paramount%2B_original_programming?lang=en)
- Amazon Prime:
  - [TV](https://wikiless.org/wiki/List_of_Amazon_Prime_Video_original_programming?lang=en)
- Youtube Prenium:
  - [TV](https://wikiless.org/wiki/List_of_YouTube_Premium_original_programming?lang=en)

## Notes on scraping

- Using `scrapy` inside a `virtualenv`
- See [here](https://scribe.rip/c%C3%B3digo-ecuador/the-better-way-to-web-scrape-tables-using-pythons-scrapy-application-9b245d5b117f) and [here](https://www.simplified.guide/scrapy/scrape-table) for table scraping
- User agents [2021](https://deviceatlas.com/blog/list-user-agent-strings-2021) or use [`scrappy-user-agents` package](https://pypi.org/project/scrapy-user-agents/) instead
- Dynamic table scraping by either using `selenium`, see [this](https://medium.com/@sarfrazarshad/scraping-dynamically-created-tables-196b7cbe6c84) or [this](https://www.geeksforgeeks.org/scrape-content-from-dynamic-websites/); or read [this](https://docs.scrapy.org/en/latest/topics/dynamic-content.html#topics-finding-data-source) to examine if it is possible with `scrapy`

