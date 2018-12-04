import pytumblr
import os
import urllib.request as urllib
import logging
import re
import json
import codecs
from tumblr_keys import *
client = pytumblr.TumblrRestClient(
    consumer_key,
    consumer_secret,
    token_key,
    token_secret
)
logging.basicConfig(filename=os.path.join(os.getcwd(), 'downloadLike.log'), level=logging.INFO, filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s')

# Number of likes to fetch in one request
limit = 20


def downloadPhotos(photos, likename):
    # downloaded.append([liked["id"], liked["reblog_key"]])
    count = 0

    # Parse photos
    for photo in photos:

        # Get the original size
        url = photo["original_size"]["url"]
        imgname = url.split('/')[-1]

        # Create a unique name
        filename = likename + "/"

        # Add numbers if more than one image
        if count > 0:
            filename += str(count) + "-"
        filename += imgname

        # Check if image is already on local disk
        if (os.path.isfile(filename)):
            print("File already exists : " + imgname)
        else:
            print("Downloading " + imgname + " from " + likename)
            urllib.urlretrieve(url, filename)
            count += 1


def downloadVideo(url, likename):
    # Get the video name
    vidname = url.split('/')[-1]
    count = 0

    # Create a unique name
    filename = likename + "/" + vidname

    # Check if video is already on local disk
    if (os.path.isfile(filename)):
        print("File already exists : " + vidname)
    else:
        print("Downloading " + vidname + " from " + likename)
        urllib.urlretrieve(url, filename)


def media_download(rmfile, directory, pages,rmidlist):
    posts = 0
    total = 0
    cnt = 0
    for page in range(0, pages):
        offset = page * limit
        likes = client.likes(offset=offset, limit=limit)["liked_posts"]

        # Parse the likes
        for liked in likes:
            cnt = cnt + 1
            id = liked['id']
            # Store in a directory based on blog name
            # Create a unique name
            blog_dir = directory + "/" + liked["blog_name"]
            if not os.path.isdir(blog_dir):
                os.mkdir(blog_dir)
            likename = blog_dir + "/" + str(id)
            if rmidlist.get(str(likename)) is not None:
                continue
            try:

                if not os.path.isdir(likename):
                    os.mkdir(likename)

                if "photos" in liked:
                    downloadPhotos(liked["photos"], likename)

                if "video_url" in liked:
                    downloadVideo(liked["video_url"], likename)

                summaryFile = 'summary'
                summary = liked['summary']
                jsonFile ='content'

                if "body" in liked:
                    # Create a unique name
                    filename = likename + "/body.htm"
                    with codecs.open(filename, "w", "utf-8") as ds:
                        ds.write(
                            '<!doctype html><html><head><meta http-equiv="content-type" content="text/html; charset=utf-8"><title></title></head><body>')
                        ds.write(liked["body"])
                        ds.write('</body></html>')
                with open(likename+'/'+summaryFile + ".txt", "w",encoding='utf8') as f:
                    f.write(summary)


                with open(likename+'/'+jsonFile + ".json", "w") as f:
                    json.dump(liked, f)

            except Exception as e:
                id = '===' + str(id)
                logging.error('===exception===EXCEPTION===id:' + str(id) + "|" + str(liked["blog_name"]) + "|" +"|"+likename+"|"+ str(e))
            print('[' + str(cnt) + ':' + str(liked['type']) + ']')
            rmfile.write(str(likename) + '\n')
            rmfile.flush()


def main():
    # downloaded ids
    rmidlist = {}
    rmuname = "doneList.txt"
    rmfile = open(rmuname, 'a')
    try:
        rmfile = open(rmuname, 'r+')
        duid = rmfile.readline().rstrip('\n')
        while (duid.strip()):
            rmidlist[duid] = 1
            duid = rmfile.readline().rstrip('\n')
    except:
        pass



    # Save dir
    dirname = 'MyLiked'
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Verbose
    info = client.info()
    # Get the content
    name = info["user"]["name"]
    number = int(info["user"]["likes"])

    # Currently the Tumblr API returns no more than 1000 likes
    pages = min(number // limit, 50)

    # Display the number of likes and pages of 20
    print("Tumblr user {0} has {1} likes".format(name, number))
    print("{0} pages will be fetched".format(pages))

    media_download(rmfile, dirname, pages,rmidlist)


if __name__ == '__main__':
    main()
    print('Done!')
