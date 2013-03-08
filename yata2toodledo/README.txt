This directory is intended to hold a Yata -> Toodledo converter.

It will accept an XML file provided by Yata and create another
XML file to be imported into an empty Toodledo account.  This
will be one way only, and without considering any previously
existing tasks...


The XML for my tasks:
http://www.toodledo.com/tools/xml.php?view=1

Toodledo tasks API: http://api.toodledo.com/2/tasks/index.php

A minimal XML file to import: u:\Documents\Toodledo\test_import.xml
<xml>
<toodledoversion>6</toodledoversion>
<item>
     <title>Buy Milk</title>
</item>
</xml>


