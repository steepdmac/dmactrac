# Development notes for dmactrac application

## To Do

- figure out how to use debugging to view variable values when application is running
  - debugging may not be necessary to add desired functionality - See Hacking Whoosh section below
  - did learn that the application doesn't pass much data around. Generally the data is either in config settings or the Whoosh cache
- add sections to this document to keep track of stuff I learn
- start using git branches for modifications
 
### Hacking Whoosh
- All synced Zotero data is stored in a Whoosh cache
- Should be able to query that to find out in advance which publications have "Relations" 
- Use Documents/Projects/whoosh-sandbox to develop code for examining the cache.


## Helpful links
[Kerko documentation][Kerko_documentation]

[Kerko]: https://github.com/whiskyechobravo/kerko
[Kerko_documentation]: https://whiskyechobravo.github.io/kerko/
[KerkoApp]: https://github.com/whiskyechobravo/kerkoapp
[KerkoApp_demo]: https://demo.kerko.whiskyechobravo.com
[Flask]: https://pypi.org/project/Flask/
[Python]: https://www.python.org/
[TOML]: https://toml.io/
[Zotero]: https://www.zotero.org/
[Zotero_demo]: https://www.zotero.org/groups/2348869/kerko_demo/items
