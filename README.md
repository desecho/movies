#Movies

The web application on Python2/Django/javascript/jQuery to create movie lists ("watched" and "to watch"), rate movies and add comments, share your lists with friends, get recommendations from friends. Works in Russian social network [htp://vk.com](htp://vk.com). [http://vk.com/app3504693_2912142](http://vk.com/app3504693_2912142). The interface is in Russian.

##Used APIs
* [TMDb](http://www.themoviedb.org/) (Requires API Key)
* [OMDb](http://www.omdbapi.com/)
* [2torrents.org](http://2torrents.org)
 
##Installation instructions

* Change/Add the following variables in settings.py:
    * DATABASES
    * TMDB_KEY
    * VK_APP_ID
    * VK_APP_SECRET
* Insert your analytics code to src/static/js/analytics.js if you'd like
* Change variable in installation_settings.sh
* Run install.sh
* Run the following commands:

```bash
mkdir cache
touch cache/tmdb3.cache
chmod 777 cache/tmdb3.cache
./manage.py migrate
./manage.py collectstatic
```
