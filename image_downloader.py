from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import os.path
import json
import urllib.request, urllib.error
import sys
import time
import argparse
import numpy as np
import colors


def intsize(x, cminus=False):
    if x > 0:
        return int(np.log10(x)) + 1
    elif x == 0:
        return 1
    else:
        if cminus:
            return int(np.log10(-x)) + 2
        else:
            return int(np.log10(-x)) + 1



def main(args):
    number_of_scrolls = args.nums // 400 + 1
    # number_of_scrolls * 400 images will be opened in the browser

    path = os.path.join(os.getcwd(), args.driver)
    # print('adding `{}` to path'.format(colors.blue(path)))
    os.environ["PATH"] += os.pathsep + path

    download_path = os.path.join(args.savepath, args.keyword.replace(" ", "_"))
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    url = args.google_domain+'/search?q='+args.keyword+'&source=lnms&tbm=isch'
    print('Opening browser with driver {}'.format(colors.green(args.driver)))
    driver = webdriver.Firefox(args.driver)

    print('Retriving images from {}'.format(colors.green(url)))
    driver.get(url)
    head = 'Mozilla/5.0 (Windows NT 6.1) ' \
           'AppleWebKit/537.36 (KHTML, like Gecko) ' \
           'Chrome/41.0.2228.0 Safari/537.36'
    headers = {'User-Agent': head}
    extensions = args.image_type.strip('').split(',')
    xpath = "//input[@value='Show more results']"
    for _ in range(number_of_scrolls):
        for __ in range(10):
            # multiple scrolls needed to show all 400 images
            driver.execute_script("window.scrollBy(0, 1000000)")
            time.sleep(0.2)
        # to load next 400 images
        time.sleep(0.5)
        try:
            driver.find_element_by_xpath(xpath).click()
        except Exception as e:
            print("Less images found: {}".format(colors.red(e)))
            break

    # imges = driver.find_elements_by_xpath('//div[@class="rg_meta"]')
    # not working anymore
    images = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    image_total = len(images)
    downloaded_images = 0
    print("Total images found: {}".format(colors.green(image_total)))
    download_pattern = 'Downloading {{:>{}}}: {{}}'.format(len(colors.green(args.nums)))
    with open(download_path+'.log', 'w') as logfile:
        logfile.write('# keyword: {}\n# url: {}\n # required images: {}\n'
                      .format(args.keyword, url, args.nums))
        for idx, image in enumerate(images):
            image_url = json.loads(image.get_attribute('innerHTML'))["ou"]
            image_type = json.loads(image.get_attribute('innerHTML'))["ity"]
            if image_type in extensions:
                print(download_pattern
                      .format(colors.green(downloaded_images+1),
                              colors.blue(image_url)))
                try:
                    req = urllib.request.Request(image_url, headers=headers)
                    raw_image = urllib.request.urlopen(req).read()
                    with open(os.path.join(download_path,
                                           str(downloaded_images)+"."+image_type),
                              "wb") as f:
                        f.write(raw_image)
                    downloaded_images += 1
                    logfile.write('{}: {}\n'
                                  .format(downloaded_images, image_url))
                except Exception as e:
                    print("Downloading failed: {}".format(colors.red(e)))
                # finally:
                #     print
                if downloaded_images >= args.nums:
                    break
    print("{} found, {} required, {} downloaded "
          .format(colors.blue(image_total),
                  colors.green(args.nums),
                  colors.red(downloaded_images)))
    driver.quit()


parser = argparse.ArgumentParser()
parser.add_argument('--driver', type=str,
                    default='drivers/firefox/v0.20.1-linux64')
parser.add_argument('--keyword', type=str,
                    default=None, required=True)
parser.add_argument('--nums', type=int, default=100)
parser.add_argument('--savepath', type=str, default='downloads')
parser.add_argument('--google-domain', type=str,
                    default='https://www.google.com')
parser.add_argument('--image-type', type=str, default='jpg,jpeg,png,gif')


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
