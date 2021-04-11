

## Gender analysis of the LCNAF

Gender data was extracted from the file "LC Name Authority File (LCNAF) *NEW Pilot* (MADS/RDF only)" downloaded from https://id.loc.gov/download/.

The download was dated 17 March 2021.

The files in this folder are ...

   * lcnaf-gender.py is the console application which extracts the gender data from the LCNAF
   * lcnaf-1k.txt is the first one thousand items (aka NAF records) from the LCNAF
   * lcnaf-1k-pretty.txt is a pretty-printed version of lcnaf-1k.txt
   * lcnaf-genders-detail.csv is the result of the analysis
   * lcnaf-genders-detail.xlsx is the .csv file converted to normal Excel format, which I'm providing for you because Excel's import of .csv files is (ahem) problematic.
   * lcnaf-genders-simple.csv is the data from lcnaf-genders-detail.csv combining identical gender values from different sources

### The analysis

In theory, you could simply scan the LCNAF and count the genders.  However, gender values are expressed in two ways:  with an id internal to the item (aka record), or with a URL.  The gender value of *both* the ids and the URLs is given within the item (aka record).  The URLs were *NOT* retrieved or checked.

In order to preserve the URLs, instead of counting gender values, I count source+gender combinations.  All local ids are labelled with a source of "$local".

Also, some items (aka records) specify a list of genders.  For these items, I combine both the source and the gender values using '+'.  For example, if the gender is given as URL-1 and URL-2 and those URLs have gender values G-1 and G-2 respectively, I would count this record using:

     source:        "URL-1+URL-2"
     gender value:  "G-1+G-2"

Again, the "detail" version of the analysis counts combinations of source and gender value, the "simple" version of the analysis counts only gender values.

## Questions?

If you have questions, please email me at carryonwilliams@gmail.com
