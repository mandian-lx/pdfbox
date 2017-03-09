%{?_javapackages_macros:%_javapackages_macros}

Name:           pdfbox
Version:        1.8.12
Release:        1
Summary:        Java library for working with PDF documents
License:        ASL 2.0
URL:            http://pdfbox.apache.org/
Source0:        http://www.apache.org/dist/pdfbox/%{version}/%{name}-%{version}-src.zip
#Don't download anything
Patch0:         %{name}-nodownload.patch
#Use sysytem bitream-vera-sans-fonts instead of bundled fonts
Patch1:         %{name}-1.2.0-bitstream.patch

Patch2:         pdfbox-1.8.11-port-to-bouncycastle1.50.patch

BuildRequires:  fonts-ttf-bitstream-vera
BuildRequires:  fontconfig
BuildRequires:  javapackages-tools
BuildRequires:  maven-local
BuildRequires:  pcfi #mvn(com.adobe.pdf:pcfi)
BuildRequires:  mvn(com.ibm.icu:icu4j)
BuildRequires:  mvn(commons-logging:commons-logging)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(log4j:log4j:1.2.17)
BuildRequires:  mvn(org.apache.ant:ant)
BuildRequires:  mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-release-plugin)
BuildRequires:  mvn(org.apache.rat:apache-rat-plugin)
BuildRequires:  mvn(org.bouncycastle:bcmail-jdk15on)
BuildRequires:  mvn(org.codehaus.mojo:javacc-maven-plugin)

BuildArch:      noarch

Requires:       java >= 1:1.6.0
Requires:       fonts-ttf-bitstream-vera

%description
Apache PDFBox is an open source Java PDF library for working with PDF
documents. This project allows creation of new PDF documents, manipulation of
existing documents and the ability to extract content from documents. Apache
PDFBox also includes several command line utilities. Apache PDFBox is
published under the Apache License v2.0.

%package examples
Summary:        Examples for %{name}

%description examples
This package contains examples for %{name}.

%package javadoc
Summary:        Javadoc for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%package ant
Summary:        Apache PDFBox for Ant

%description ant
%{summary}.

%package -n fontbox
Summary:        Apache FontBox

%description -n fontbox
FontBox is a Java library used to obtain low level information from font
files. FontBox is a subproject of Apache PDFBox.

%package -n jempbox
Summary:        Apache JempBox

%description -n jempbox
JempBox is an open source Java library that implements Adobe's XMP(TM)
specification. JempBox is a subproject of Apache PDFBox.

%package parent
Summary:        Apache PDFBox Parent POM

%description parent
Apache PDFBox Parent POM.

%package reactor
Summary:        Apache PDFBox Reactor POM

%description reactor
Apache PDFBox Reactor POM.

%package -n preflight
Summary:        Apache Preflight

%description -n preflight
The Apache Preflight library is an open source Java tool that implements 
a parser compliant with the ISO-19005 (PDF/A) specification. Preflight is a 
subproject of Apache PDFBox.

%package -n xmpbox
Summary:        Apache XmpBox

%description -n xmpbox
The Apache XmpBox library is an open source Java tool that implements Adobe's
XMP(TM) specification.  It can be used to parse, validate and create xmp
contents.  It is mainly used by subproject preflight of Apache PDFBox. 
XmpBox is a subproject of Apache PDFBox.

%prep
%setup -q
find -name '*.class' -delete
find -name '*.jar' -delete

%patch0 -p1 -b .nodownload
%patch1 -p1 -b .bitstream
%patch2 -p1 -b .bouncycastle1.50
sed -i.bcprov1.54 "s|algorithmidentifier.getObjectId().getId()|algorithmidentifier.getAlgorithm().getId()|" \
 pdfbox/src/main/java/org/apache/pdfbox/pdmodel/encryption/PublicKeySecurityHandler.java

sed -i 's/BUILD_PARSER=false/BUILD_PARSER=true/' preflight/src/main/javacc/pdf_extractor.jj

%pom_disable_module war
#Disable lucene, not compatible with lucene 3.6
%pom_disable_module lucene
# Don't build app (it's just a bundle of everything)
%pom_disable_module preflight-app
%pom_disable_module app

%pom_remove_plugin -r :animal-sniffer-maven-plugin
%pom_remove_plugin -r :maven-deploy-plugin
# cobertura-maven-plugin has been retired
%pom_remove_plugin :cobertura-maven-plugin preflight
%pom_remove_dep javax.activation:activation preflight

%pom_change_dep -r :ant-nodeps :ant
%pom_change_dep -r :log4j ::1.2.17

#Fix line endings
sed -i -e 's|\r||' RELEASE-NOTES.txt
#Remove META-INF file that does not exist

#Use jdk15on version of bcprov
%pom_change_dep -r :bcmail-jdk15 :bcmail-jdk15on:1.50
%pom_change_dep -r :bcprov-jdk15 :bcprov-jdk15on:1.50
%pom_add_dep org.bouncycastle:bcpkix-jdk15on:1.50 %{name}

sed -i -e '/META-INF/d' pdfbox/pom.xml
#Remove included fonts
rm -r pdfbox/src/main/resources/org/apache/pdfbox/resources/ttf

# TODO
rm -rf examples/src/main/java/org/apache/pdfbox/examples/signature/CreateSignature.java \
 examples/src/main/java/org/apache/pdfbox/examples/signature/CreateVisibleSignature.java \
 examples/src/test/java/org/apache/pdfbox/examples/pdfa/CreatePDFATest.java
# IllegalArgumentException: Parameter 'directory' is not a directory
rm -r preflight/src/test/java/org/apache/pdfbox/preflight/integration/TestValidFiles.java

# Skip testImageIOUtils
# https://issues.apache.org/jira/browse/PDFBOX-2084
sed -i -e "/TestImageIOUtils.java/d" pdfbox/pom.xml
# Remove unpackaged deps for the above tests
%pom_remove_dep net.java.dev.jai-imageio:jai-imageio-core-standalone pdfbox
# https://bugzilla.redhat.com/show_bug.cgi?id=1094417
%pom_remove_dep com.levigo.jbig2:levigo-jbig2-imageio pdfbox
rm -rf pdfbox/src/test/java/org/apache/pdfbox/util/TestImageIOUtils.java \
 pdfbox/src/test/java/org/apache/pdfbox/pdmodel/graphics/xobject/PDJpegTest.java \
 pdfbox/src/test/java/org/apache/pdfbox/pdmodel/graphics/xobject/PDCcittTest.java
sed -i -e /PDJpegTest/d pdfbox/src/test/java/org/apache/pdfbox/TestAll.java
sed -i -e /PDCcittTest/d pdfbox/src/test/java/org/apache/pdfbox/TestAll.java
sed -i -e /TestImageIOUtils/d pdfbox/src/test/java/org/apache/pdfbox/TestAll.java

# com.googlecode.maven-download-plugin:download-maven-plugin:1.2.1 used for get 
# test resources: http://www.pdfa.org/wp-content/uploads/2011/08/isartor-pdfa-2008-08-13.zip
%pom_remove_plugin :download-maven-plugin preflight

# Disable filtering
sed -i -e /filtering/d examples/pom.xml

# install all libraries in _javadir
%mvn_file :jempbox jempbox
%mvn_file :%{name} %{name}
%mvn_file :%{name}-ant %{name}-ant
%mvn_file :%{name}-examples %{name}-examples
%mvn_file :preflight preflight
%mvn_file :xmpbox xmpbox
%mvn_file :fontbox fontbox

%build

%mvn_build -s -- -Dadobefiles.jar=$(build-classpath pcfi)

%install
%mvn_install

%files -f .mfiles-%{name}
%doc README.txt RELEASE-NOTES.txt

%files examples -f .mfiles-%{name}-examples
%files ant -f .mfiles-%{name}-ant

%files -n fontbox -f .mfiles-fontbox
%doc fontbox/README.txt
%doc LICENSE.txt NOTICE.txt

%files -n jempbox -f .mfiles-jempbox
%doc jempbox/README.txt
%doc LICENSE.txt NOTICE.txt

%files parent -f .mfiles-%{name}-parent
%doc LICENSE.txt NOTICE.txt

%files reactor -f .mfiles-%{name}-reactor
%doc LICENSE.txt NOTICE.txt

%files -n preflight -f .mfiles-preflight
%doc preflight/README.txt

%files -n xmpbox -f .mfiles-xmpbox
%doc xmpbox/README.txt
%doc LICENSE.txt NOTICE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Mon Aug 29 2016 Michael Simacek <msimacek@redhat.com> - 1.8.12-2
- Workaround JAVACC-292 bug

* Fri May 27 2016 gil cattaneo <puntogil@libero.it> 1.8.12-1
- update to 1.8.12

* Fri Apr 08 2016 gil cattaneo <puntogil@libero.it> 1.8.11-2
- rebuilt with bcmail 1.54

* Mon Feb 08 2016 gil cattaneo <puntogil@libero.it> 1.8.11-1
- update to 1.8.11

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Sep 05 2015 gil cattaneo <puntogil@libero.it> 1.8.10-1
- update to 1.8.10

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Mar 24 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.8.8-4
- Remove cobertura-maven-plugin usage from POM
- Resolves: rhbz#1205176

* Wed Feb 11 2015 gil cattaneo <puntogil@libero.it> 1.8.8-3
- introduce license macro

* Mon Jan 19 2015 gil cattaneo <puntogil@libero.it> 1.8.8-2
- rebuilt for regenerate rpm {osgi,maven}.prov, {osgi,maven}.req

* Sat Jan 17 2015 gil cattaneo <puntogil@libero.it> 1.8.8-1
- update to 1.8.8

* Thu Oct 30 2014 gil cattaneo <puntogil@libero.it> 1.8.7-1
- update to 1.8.7

* Fri Sep 26 2014 gil cattaneo <puntogil@libero.it> 1.8.5-3
- build fix for bouncycastle 1.50 (rhbz#1100445)
- adapt to current guideline
- remove lucene sub package
- force log4j12 usage

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 21 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.5-1
- Add patch to disable test that needs missing deps
- Remove missing test deps from pdbbox pom
- Use junit instead of junit4

* Fri May 2 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.5-1
- Update to 1.8.5

* Sat Feb 1 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.4-1
- Update to 1.8.4

* Mon Dec 2 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.3-1
- Update to 1.8.3
- New pcfi.jar location

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Jul 14 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.2-1
- Update to 1.8.2
- Drop unneeded maven BRs

* Wed Apr 17 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.1-1
- Update to 1.8.1

* Thu Mar 28 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.0-1
- Update to 1.8.0
- Add preflight and xmpbox sub-packages

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.7.0-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Sep 24 2012 Orion Poplawski <orion@cora.nwra.com> - 1.7.0-4
- Drop lucene sub-package for now, not compatible with lucene 3.6

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 3 2012 Orion Poplawski <orion@cora.nwra.com> - 1.7.0-2
- Fix javadocs -> javadoc typo

* Tue Jul 3 2012 Orion Poplawski <orion@cora.nwra.com> - 1.7.0-1
- Update to 1.7.0
- Add examples sub-package
- Add BR on bitstream font and fontconfig

* Wed Apr 18 2012 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-5
- Drop pdfbox-app sub-package, nothing but a bundle (bug #813712)

* Wed Feb 1 2012 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-4
- Add proper provides/obsoletes to javadoc sub-package (bug #785396)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Oct 24 2011 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-2
- BR separately packaged pcfi

* Wed Aug 10 2011 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-1
- Update to 1.6.0
- Add pcfi-2010.08.09.jar to sources
- Drop depmap
- Use apache-commons-logging
- Other cleanup

* Fri Jun 3 2011 Orion Poplawski <orion@cora.nwra.com> - 1.5.0-2
- Use maven 3
- Single javadoc package

* Thu Mar 10 2011 Orion Poplawski <orion@cora.nwra.com> - 1.5.0-1
- Update to 1.5.0

* Tue Dec 28 2010 Orion Poplawski <orion@cora.nwra.com> - 1.4.0-2
- Create sub-packages
- Use depmap file

* Tue Dec 21 2010 Orion Poplawski <orion@cora.nwra.com> - 1.4.0-1
- Update to 1.4.0

* Sat Nov 6 2010 Orion Poplawski <orion@cora.nwra.com> - 1.3.1-1
- Update to 1.3.1

* Fri Aug 13 2010 Orion Poplawski <orion@cora.nwra.com> - 1.3.0-0.1
- Update to 1.3.0-SNAPSHOT

* Thu Jul 15 2010 Orion Poplawski <orion@cora.nwra.com> - 1.2.1-1
- Update to 1.2.1

* Thu Jul 1 2010 Orion Poplawski <orion@cora.nwra.com> - 1.2.0-1
- Update to 1.2.0
- Drop gcj support

* Mon Oct 19 2009 Orion Poplawski <orion@cora.nwra.com> - 0.8.0-2
- Add Requires

* Thu Oct 15 2009 Orion Poplawski <orion@cora.nwra.com> - 0.8.0-1
- Initial Fedora package
