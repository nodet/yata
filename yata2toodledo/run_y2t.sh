java org.apache.xalan.xslt.Process -IN tests/yata.xml -XSL y2t.xml -out tests/too.out.xml
diff tests/too.xml tests/too.out.xml