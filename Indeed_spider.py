import scrapy
from scrapy.crawler import CrawlerProcess
import datetime

class IndeedSipder(scrapy.Spider):
    name = "IndeedCanadaSpider"

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'Data.csv',
    }

    tod = datetime.datetime.now()

    with open("towns.txt") as f:
        cities = f.readlines()

    def start_requests(self):
        for city in self.cities:
            yield scrapy.Request(url="https://ca.indeed.com/jobs?q=&l=" + city + "&radius=100&sort=date",
                                 callback=self.parse, dont_filter=True,
                             headers={
                                 'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                             },
                             )


    def parse(self, response):
        jobs = response.css("div.jobsearch-SerpJobCard")
        for job in jobs:
            link = job.css("h2.title > a::attr(href)").extract_first()
            if "clk" in link:
                link = link[7:]
                link = "https://ca.indeed.com/viewjob" + link
            else:
                link = "https://ca.indeed.com" + link

            title = job.css("h2.title > a::text").extract_first()

            company = job.css("span.company > a::text").extract_first()
            if not company:
                company = job.css("span.company::text").extract_first()

            location = job.css("span.location::text").extract_first()

            salary = job.css("span.salaryText::text").extract_first()
            if not salary:
                salary = "N/A"

            date = job.css("span.date ::text").extract_first()
            if date == "Just posted" or date == "Today":
                calDate = self.tod.date()
            else:
                calDate = date.split()[0]
                if calDate == "30+":
                    calDate = "30"
                calDate = datetime.timedelta(days=int(calDate))
                calDate = self.tod - calDate
                calDate = calDate.date()

            yield {
                "Job Title": title.strip(),
                "Company": company.strip(),
                "Location": location.strip(),
                "Salary": salary.strip(),
                "Posted": date.strip(),
                "Date": str(calDate),
                "URL / Link": link
            }

        nextPage = response.css("ul.pagination-list > li")
        if nextPage:
            nextPage = nextPage[-1].css("a::attr(href)").extract_first()
            if nextPage:
                yield scrapy.Request("https://ca.indeed.com" + nextPage,
                                     callback=self.parse, dont_filter=True,
                                     headers={
                                         'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                                     },
                                     )



process = CrawlerProcess()
process.crawl(IndeedSipder)
process.start()
