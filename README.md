# Movies

The interface is available in Russian and English.

Temporary not working: Share your lists with friends, get recommendations from friends. Available on [VK](http://vk.com/app3504693_2912142).

## Used APIs
* [TMDb](http://www.themoviedb.org/) (Requires API Key)
* [OMDb](http://www.omdbapi.com/)
 
## Installation instructions

* Change/Add the following variables in settings.py:
    * DATABASES
    * TMDB_KEY
    * VK_APP_ID
    * VK_APP_SECRET
* Insert your analytics code to src/static/js/analytics.js if you'd like
* Change the variable in installation_settings.sh
* Run install.sh
* Run the following commands:

```bash
mkdir cache
touch cache/tmdb3.cache
chmod 777 cache/tmdb3.cache
./manage.py migrate
./manage.py collectstatic
```
