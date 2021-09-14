import scrapy


class HotelsSpider(scrapy.Spider):
    name = 'hotels'
    allowed_domains = ['hotels.ng']
    start_urls = ['https://hotels.ng']

    def parse(self, response):

        #Follow state page links
        hotels_by_city_page_links = response.css("div.states-grid div a::attr(href)")
        yield from response.follow_all(hotels_by_city_page_links, self.parse)

        #Follow hotel links on each state page
        hotel_links = response.css('div.listing-hotels-details-property a::attr(href)')
        yield from response.follow_all(hotel_links, self.parse_hotel)
        
        #Follow pagination links
        pagination_links = response.css("ul.pagination li a::attr('href')")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_hotel(self, response):
        def remove_html(text):
            import re
            clean = re.compile("<.*?>|\r\n|[\xa0]")
            return re.sub(clean, ' ', text).strip()
   
        address = ''
        desc = ''

        for p in response.css("p.sph-header-address"):
                address = p.get()

        for p in response.css('article.sph-info-details'):
                desc = p.get()
        
        hotel_info = {

            'name': response.css("h1.sph-header-name::text").get(),
            'address': remove_html(address),
            'facilities': response.css('div.sph-info-facility p::text').getall(),
            'desc': remove_html(desc),
            'price':  response.css("p.sph-room-price::text").getall()
        }

        yield hotel_info
        
        #Follow review page links
        review_link = response.css("div.sph-hotel-reviews a.sph-reviews-more::attr(href)")
        yield from response.follow_all(review_link, self.parse_review)


    def parse_review(self, response):
        review_info = {
            'hotel reviewed': response.css('div.sph-header h1.sph-header-name::text').get(),
            'address': response.css("p.sph-header-address::text").getall(), 
            'reviewers': response.css("div.all_reviews_list article.sph-reviews-individual p.sph-reviews-person::text").getall(),
            'ratings': response.css("div.all_reviews_list h5 span::text").getall(),
            'reviews': response.css("div.all_reviews_list article.sph-reviews-individual p:nth-child(4)::text").getall()
        }

        return review_info
