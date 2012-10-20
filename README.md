# DJ-BaseSite

DJ-BaseSite is a base Django **development** website project that adds basic user interaction to the site. Features include: The Django admin site, a login and logout system, a user registration system with required activation (via email), deactivation (an option during activation) and account recovery.

#### _This project is currently in the Alpha phase. Therefore it is suggested you thoroughly read and test when forking, etc._

DJ-BaseSite was written with [Python 2.7](http://www.python.org/download/releases/2.7/) and [Django 1.4](https://www.djangoproject.com/download/) on Windows 7 Home Premium 64 bit (Service Pack 1)

## License
DJ-BaseSite is released under the New BSD License, refer to the LICENSE file in the root of the repository before continuing.

## Change Log

### `0.7` (Oct 20, 2012)
* Added the deactivation and account recovery systems.
* Variable `EMAIL_MESSAGE` was replaced with `ACTIVATE_EMAIL` & `RECOVERY_EMAIL` was added. 
* The `response` variable was changed in all views to the correct spelling. derp.
* Function `clean_emailRE()` was added to `validation.py`
* The function `UserActivationKey()` in `views.py` was renamed to `KeyGen()`

### [`0.5`](https://github.com/Kris619/DJ-BaseSite/zipball/80cdb11749afa9d2ecfcbb0a91f3f867f183bfc3) (Oct 13, 2012) SHA: 80cdb11749afa9d2ecfcbb0a91f3f867f183bfc3
* login / registration system with Django's default authentication backend
* activation system (deactivation system not implemented)
* reCAPTCHA support for registration

## Quick Start
1. Open up the `config.txt` file and change the data under `CUSTOM VARIABLES` to your information. The configuration is explained below.
2. Execute the `SetupProject.py` script and enter a project name, it will replicate the project out of `/myproject/` to `/yourproject/` with your information.
3. Run syncdb via terminal/console in the root of the project: `python manage.py syncdb`
    * Windows users will need to add the path of their Python 2.7 installation (example: `C:/Python27/`) to the [path variable](http://showmedo.com/videotutorials/video?name=960000&fromSeriesID=96)
4. Run the development server: `python manage.py runserver`

> You should be done at this point. So check out your new website at [http://localhost:8000](http://localhost:8000) or [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Configuration

* `baseurl`
    * Used to create activation, deactivation and recovery links
* `admin_name/email` `(`[`official documentation`](https://docs.djangoproject.com/en/1.4/ref/settings/#admins)`)`
    * Adds a name and email to the ADMINS tuple in settings. On an error your website will email you logged errors.
* `secret_key` `(`[`official documentation`](https://docs.djangoproject.com/en/1.4/ref/settings/#secret-key)`)`
    * A secure string used to provide cryptographic signing. It is automatically added to a [default Django project](https://docs.djangoproject.com/en/dev/intro/tutorial01/#creating-a-project) in settings.
* `captcha_publickey/privatekey`
    * DJ-BaseSite uses [reCAPTCHA](http://www.google.com/recaptcha/learnmore) to prevent bots from creating accounts, so you'll need to [get a private and public key from the website](http://www.google.com/recaptcha)
* `HOSTsmtp`
    * The SMTP server
* `HOSTemail`
    * The email address
* `HOSTpass`
   * HOSTemail's password