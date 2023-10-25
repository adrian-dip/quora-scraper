# Quora scraper

Quora scraper (works as of Jan. 2023). The script can scrape questions from a topic (https://www.quora.com/topic/Finance -> ['https://www.quora.com/Using-technical-analysis-do-you-think-the-S-P-500', ...]) and then scrape the answers. If you already have links pointing to questions, you can also use this code (see the option "question_links" below).

The script saves the questions, answers, and engagement metrics (votes, comments, shares, and views) to a .csv file. It also saves links to related questions in a separate .pkl file for future scraping. 

The script does not have console options so that you can run it from a pipeline or Shell or whatever you wish with minimal changes. 

## Scraping options

### Example

```
if __name__ == "__main__":
    main(topics=['China', 'Economics'], save_dir="C:/data/quora/")
```

### topics=None 

Optional. Expected input: list. Example: ['Computer_science', 'Physics']

### question_links=None 
Optional. Expected input: list. Links to questions if you already scraped topics or are using data from your own sources.

### save_dir = None
Expected input: str. Save directory. To save in the same directory you're running the script, please set to "".

### save_frequency_main=100 
Expected input: int. Save when the number of questions scraped >= than this value. Set to a lower number if you have an unstable internet connection, or a higher number if you want fewer but larger files.


### previous_save_number=0
Expected input: int. The total number of questions scraped is part of the save name. If the program hangs, you can resume scraping without rewriting or duplicating files using this kwarg. If you want to automate this, you can always do 
```
files = glob.glob(save_dir + '*.csv')
files = [int(i.group(0)) for i in map(re.compile(r'\d+').search, files)]
previous_save_number = max(files)
```
But please be aware that this will default to 0 if you run a new instance on the cloud and will produce overwrite errors when you consolidate the data.

### get_views=False

Due to Quora's anti-scraping measures, we have to go through hoops to get the viewcount. This makes the program unstable, which is why when get_views=True, we use the multiprocessing module to time out the script because it has a 6% failure rate. This means much slower scraping as the script always runs for 240 seconds per page before ending the execution. When get_views=False, the program is much faster because it starts with a new question a couple of seconds after it finishes scraping the previous page.

Consider leaving this argument as False or running several scripts at the same time if you really need the views.


## Important notice
get_views=True results in much slower scraping. If you find a way to evade the antiscraping algo or have an idea to improve efficiency, please feel free to message me or make a pull request!.

## License
Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0) 

https://creativecommons.org/licenses/by-nc/3.0/
