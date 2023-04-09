import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import time

from selenium import webdriver

# 반드시 확인!! 스팀 Kaggle 데이터 읽기  경로만 본인 환경에 맞게 재설정
a_dataframe = pd.read_csv('C:/Users/raven/git/gameChanger/dataset/games.csv') 
# AppID 속성 추출한 데이터프레임
game_no = a_dataframe['AppID']

# 뽑아내야 할 데이터들 태그 정리 및 리스트
#  metacritic URL 주소 링크 (div id=game_area_metalink  a href)

#  metacritic 페이지에 안에서 가져와야 할 것  
# summary (li class=summary_detail product_summary  span class=data)
# Genre(s) (ul class=summary_details  li class=summary_detail product_genre  span class=data)
# critic reviews (ol class=reviews critic_reviews  li class=review critic_review first_review & li class=review critic_review & li class=review critic_review last_review)
# user reviews (ol class=reviews user_reviews  li class=review user_review first_review & li class=review user_review & li class=review user_review last_review)

# 스팀 페이지에서 가져와야 할 것 (완료)
# CUSTOMER REVIEWS (div class=summary_section  span class=game_review_summary)
# Overall Review
# Recent Reviews 
# MOST HELPFUL REVIEWS (div id=user_reviews_container) 
# Currently popular(지금 유행중인 게임인지 여부) (div class=block responsive_apppage_details_right recommendation_reasons  p class=reason for) 

# first_idx - 탐색 시작할 인덱스 번호  result - 결과값 담을 배열
def start_crawling(first_idx, result):
  driver = webdriver.Chrome('C:\\Users\raven\git\gameChanger\WebDriver\chromedriver.exe') # chromedriver 연결

  for no in range(first_idx, len(game_no)+1):
    ### URL 가져오기 시작 ###
    url = 'https://store.steampowered.com/app/%d' %(int(game_no[no]))
    print(url)
    driver.get(url)
    time.sleep(3)
    html = urllib.request.urlopen(url)
    driver.execute_script("window.scrollTo(0, 5000);") # 스크롤 내린 상태로 Parsing 진행
    time.sleep(10)
    html = driver.page_source
    SoupUrl = BeautifulSoup(html, 'html.parser')
    ### URL 가져오기 끝 ###
    
    tag_name_overall_reviews = SoupUrl.find('div', attrs={'id':'review_histogram_rollup_section'}) # Overall Reviews 정보
    tag_name_recent_reviews = SoupUrl.find('div', attrs={'id':'review_histogram_recent_section'}) # Recent Reviews 정보

    ### Overall Review 및 recent_review 데이터 추출 시작 ###
    try:
      overall_reviews = tag_name_overall_reviews.find('span', attrs={'class':'game_review_summary'})
      overall_reviews = overall_reviews.get_text()

      recent_reviews = tag_name_recent_reviews.find('span', attrs={'class':'game_review_summary'})
      recent_reviews = recent_reviews.get_text()
    except:
      print("Overall Review 또는 Recent Review 데이터가 없습니다.")
    ### Overall Review 및 recent_review 데이터 추출 끝 ###
    ### metacritic URL 주소 추출 시작 ###
    try:
      metacritic_url = SoupUrl.find('div', attrs={'id':'game_area_metalink'})
      metacritic_url = metacritic_url.find('a')['href']
    except:
      print("Metacritic 링크가 존재하지 않습니다.")
    ### metacritic URL 주소 추출 끝 ###
    ### 리뷰 부분 시작 ###
    reviews_total = []
    try:
      # 리뷰있는 부분 찾기
      tag_name_most_helpful_reviews = SoupUrl.find('div', attrs={'id':'Reviews_summary', 'class':'user_reviews_container'})    
      most_helpful_reviews = tag_name_most_helpful_reviews.select("div>div.leftcol>div.review_box")

      for c_review in most_helpful_reviews:
        rec = c_review.find("div", attrs={'class':'title ellipsis'}).get_text() # 추천 or 비추천
        content = c_review.find("div", attrs={'class':'content'}).get_text() # 리뷰 내용

        customer_review = rec + ", "  + content
        reviews_total.append(customer_review)
    except:
      print("리뷰가 없습니다.")
    ### 리뷰 부분 종료 ###

    steam_value = [overall_reviews] + [recent_reviews] + [metacritic_url] + [reviews_total]
    print(steam_value)
    result.append(steam_value)


def main():
  result=[]
  start_crawling(0, result) # 임시로 0번째 인덱스(처음)부터 시작하게끔 설정한 상태
  Wcrawling_tbl = pd.DataFrame(result, columns=('Overall Reviews', 'Recent Reviews', 'Most Helpful Reviews', 'Currently popular'))
  Wcrawling_tbl.to_csv('CUsersravengitgameChangerdatasetsteamGames.csv', encoding='cp949', mode='w', index=True)
  del result[:]

if __name__ == '__main__':
  main()