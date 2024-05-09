import argparse
import getpass
import yaml
import time
import re

import ebooklib.epub
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class book:
    def __init__(self, title, author, language='en'):
        self.book = ebooklib.epub.EpubBook()
        self.book.add_author(author)
        self.book.set_title(title)
        self.book.set_language(language)
        self.chapters = []

    def add_chapter(self, title, content):
        chapter_number = len(self.chapters) + 1
        chapter = ebooklib.epub.EpubHtml(
            title=title,
            file_name=f'chap_{chapter_number:02d}.xhtml'
            )
        c = f"<h1>{title}</h1>\n" + content
        chapter.set_content(c)
        self.chapters.append(chapter)

    def finalize(self):
        for x in self.chapters:
            self.book.add_item(x)
        self.book.toc = tuple(self.chapters)
        self.book.spine = self.chapters
        self.book.add_item(ebooklib.epub.EpubNcx())
        self.book.add_item(ebooklib.epub.EpubNav())
        title = self.book.title.replace(' ', '_') + '.epub'
        ebooklib.epub.write_epub(title, self.book)

def main(args):
    if args.chrome:
        driver = webdriver.Chrome()
    elif args.firefox:
        driver = webdriver.Firefox()
    else:
        raise ValueError("Must set either firefox or chrome as your browser")
    with open(args.story_yaml, 'r') as fd:
        story_list = yaml.safe_load(fd)

    if args.story not in story_list['stories']:
        raise argparse.ArgumentError(message="Story Requested is not a choice")
    chapter_blacklist = story_list['blacklist'] if 'blacklist' in story_list and story_list['blacklist'] else []

    newbook = book(args.story, story_list['creator']['name'], 'en')
    sess = requests.Session()
    try:
        if not args.password:
            pw = getpass.getpass('Patreon Password: ')
        else:
            pw = args.password
        driver.get('https://www.patreon.com/QuietValerie') # Choose a site with age verification to ensure it happens
        age = driver.find_element(By.CSS_SELECTOR, "button[data-tag='age-confirmation-button']")
        age.send_keys(Keys.RETURN)
        login = driver.find_element(By.LINK_TEXT, 'Log in')
        login.click()
        driver.implicitly_wait(20)
        email = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email.send_keys(args.username)
        email.submit()
        time.sleep(5)
        password = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password.send_keys(pw)
        password.submit()
        time.sleep(5)

        driver.get(f'https://www.patreon.com/{story_list["creator"]["name"]}')
        # the creator id is the campaign id, it can be obtained from the __NEXT_DATA__ json, or any author media, such as the pfp
        # parsing the fucked up patreon source requires html5lib, bc html.parser and lxml cant deal with their shit, for the sake of easier tooling we use this
        author_picture_url = driver.find_element(By.ID, 'avatar-image').get_attribute('src')
        author_id = re.search(r'patreon-media/p/campaign/(\d+)/', author_picture_url).group(1)
        list_of_chapters = f'https://www.patreon.com/api/posts?include=campaign,access_rules,attachments,audio,images,media,poll.choices,poll.current_user_responses.user,poll.current_user_responses.choice,poll.current_user_responses.poll,user,user_defined_tags,ti_checks&fields[campaign]=currency,show_audio_post_download_links,avatar_photo_url,earnings_visibility,is_nsfw,is_monthly,name,url&fields[post]=change_visibility_at,comment_count,content,current_user_can_comment,current_user_can_delete,current_user_can_view,current_user_has_liked,embed,image,is_paid,like_count,meta_image_url,min_cents_pledged_to_view,post_file,post_metadata,published_at,patreon_url,post_type,pledge_url,thumbnail_url,teaser_text,title,upgrade_url,url,was_posted_by_campaign_owner,has_ti_violation&fields[post_tag]=tag_type,value&fields[user]=image_url,full_name,url&fields[access_rule]=access_rule_type,amount_cents&fields[media]=id,image_urls,download_url,metadata,file_name&filter[campaign_id]={author_id}&filter[contains_exclusive_posts]=true&filter[is_draft]=false&filter[tag]={args.story}&sort=published_at&json-api-version=1.0'
        cookies = driver.get_cookies()
        for x in cookies:
            sess.cookies.set(x['name'], x['value'])
        more_chapters = True
        while more_chapters:
            req = sess.get(list_of_chapters)
            req.raise_for_status()
            j = req.json()
            for x in j['data']:
                attr = x['attributes']
                if attr['title'] in chapter_blacklist:
                    print(f"skipping {attr['title']} from blacklist")
                    continue
                if not 'content' in attr:
                    print(f"adding {attr['title']} failed, post is LOCKED")
                    continue
                print(f"adding {attr['title']}")
                newbook.add_chapter(attr['title'], attr['content'])
            try:
                list_of_chapters = j['links']['next']
            except KeyError:
                more_chapters = False

        newbook.finalize()
    except:
        raise
    finally:
        driver.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    browser_parser = parser.add_mutually_exclusive_group(required=True)
    browser_parser.add_argument('-c', '--chrome', action='store_true')
    browser_parser.add_argument('-f', '--firefox', action='store_true')
    userpass_parser = parser.add_argument_group('Username / Password')
    userpass_parser.add_argument('--username', required=True)
    userpass_parser.add_argument('--password')
    parser.add_argument('story_yaml')
    parser.add_argument('story')
    args = parser.parse_args()
    main(args)