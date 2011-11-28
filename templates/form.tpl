<!DOCTYPE html>
<html lang="en" dir="ltr" id="modernizr-com" class="no-js">
    <head>
        <title>{% block title %}{{ title }}{% endblock %} | Django Forms Five</title>
        <meta charset="utf-8">
        <base href="{{ THEIRRY_ADMIN }}">
        <meta name="description" content="">
        <meta name="author" content="Odd Sketch, LLC.">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="omni_page" content="Odd Sketch, LLC>">
        <meta name="viewport" content="user-scalable=yes, width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <meta name="application-name" content="Theirry Content Management">
        <meta http-equiv="x-ua-compatible" content="ie=edge;ff=4;chrome=8;OtherUA=5">
        <meta http-equiv="content-script-type" content="text/javascript">
    </head>
        <body>
                <form method="post" action="." accept-charset="utf-8" class="searchform">
                        {{ form.as_p }}
                </form>
        </body>
</html>