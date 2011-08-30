#!/usr/bin/env python

from __future__ import print_function
from shutil import copyfile, rmtree
from string import Template
from subprocess import Popen, PIPE
import os.path
import re
import sys


CONFIGURE_SH_IN = """\
#!/bin/bash
# This file was generated automatically.
# Please edit buildsystem/autotools/autogen.py rather than this file.

PRODUCT=@PRODUCT_UPPERCASE@
Product=@PRODUCT_MIXEDCASE@
product=@PRODUCT_LOWERCASE@
ProductSpace="@PRODUCT_MIXEDCASE_SPACED@"

VERSION=@VERSION@

INSTALLATION_SUPPORTED=@INSTALLATION_SUPPORTED@
STATIC_BUILD_SUPPORTED=@STATIC_BUILD_SUPPORTED@

PACKSCRIPTS_DIR=../admin/packscripts

hide_symbols=yes
shared=yes
debug=no
release=yes
prefix=
unittests=no

[ -d $PACKSCRIPTS_DIR ] && unittests=yes

function die {
    echo "$1" 1>&2
    exit 1
}

function check_license {

    [ -d $PACKSCRIPTS_DIR ] && return 0 
    [ -f .license.accepted ] && return 0

    if [ -f LICENSE.GPL.txt -a -f LICENSE.US.txt -a -f LICENSE.txt ] ; then
        echo
        echo "Please choose your license."
        echo
        echo "Type 1 for the GNU General Public License (GPL)."
        echo "Type 2 for the $ProductSpace Commercial License for USA/Canada."
        echo "Type 3 for the $ProductSpace Commercial License for anywhere outside USA/Canada."
        echo "Anything else cancels."
        echo
        echo -n "Select: "
        read license

    elif [ -f LICENSE.GPL.txt ] ; then
        license="1"

    elif [ -f LICENSE.US.txt ] ; then
        license="2"

    elif [ -f LICENSE.txt ] ; then
        license="3"
    else
        die "Couldn't find license file, aborting"
    fi

    if [ "$license" = "1" ]; then
        license_name="GNU General Public License (GPL)"
        license_file=LICENSE.GPL.txt
    elif [ "$license" = "2" ]; then
        license_name="$ProductSpace USA/Canada Commercial License"
        license_file=LICENSE.US.txt
    elif [ "$license" = "3" ]; then
        license_name="$ProductSpace Commercial License"
        license_file=LICENSE.txt
    else
        return 1
    fi

    while true ; do
	cat <<EOF

License Agreement

You are licensed to use this software under the terms of
the $license_name.

Type '?' to view the $license_name
Type 'yes' to accept this license offer.
Type 'no' to decline this license offer.

Do you accept the terms of this license?
EOF
        read answer

	[ "$answer" = "no" ]  && return 1
	[ "$answer" = "yes" ] && touch .license.accepted && return 0
	[ "$answer" = "?" ]   && more $license_file
    done
}

if ! check_license ; then
    die "You are not licensed to use this software."
fi

function usage {
    [ -z "$1" ] || echo "$0: unknown option \"$1\"" 1>&2
    echo "usage: $0 [options]" 1>&2
    cat <<EOF 1>&2
where options include:

EOF
if [ "$INSTALLATION_SUPPORTED" = "true" ]; then
    cat <<EOF 1>&2
  -prefix <path>
      install $ProductSpace into <path>
EOF
fi  
cat <<EOF 1>&2

  -release / -debug
      build in debug/release mode
EOF
if [ "$STATIC_BUILD_SUPPORTED" = "true" ]; then
  cat <<EOF 1>&2

  -static / -shared
      build static/shared libraries
EOF
fi
cat <<EOF 1>&2

  -[no-]hide-symbols (Unix only)
      reduce the number of exported symbols

  -[no-]unittests
      enable/disable compiled-in unittests

  -spec <mkspec>
      compile $ProductSpace for specific Qt-supported target <mkspec>

EOF
    exit 1
}

if [ -z "$QTDIR" ] ;  then
    QTDIR="$(qmake -query QT_INSTALL_PREFIX)"
    if [ $? -ne 0 ] ; then
	QTDIR=
    fi
fi

[ -z "$QTDIR" ] && die "You need QTDIR defined, or qmake in the PATH"

while [ $# -ne 0 ] ; do
    case "$1" in
	-prefix)
            if [ "$INSTALLATION_SUPPORTED" != "true" ]; then
	      echo "Installation not supported, -prefix option ignored" 2>&1
#	      usage
	    fi
	    shift
            if [ $# -eq 0 ] ; then
		    echo "-prefix needs an argument" 2>&1
		    usage
	    fi
            prefix="$1"
	    ;;
        -no-hide-symbols)
            hide_symbols=no
            ;;
        -hide-symbols)
            hide_symbols=yes
            ;;
        -override-version) # undocumented by design
            shift
            if [ $# -eq 0 ] ; then
                    echo "-override-version needs an argument" 2>&1
                    usage
            fi
            VERSION="$1"
            ;;
	-no-unittests)
	    unittests=no
	    ;;
	-unittests)
	    unittests=yes
	    ;;
        -shared)
            shared=yes
            ;;
        -static)
            if [ "$STATIC_BUILD_SUPPORTED" != "true" ]; then
                echo "Static build not supported, -static option not allowed" 2>&1
                usage
            fi
            shared=no
            ;;
        -debug)
            debug=yes
            release=no
            ;;
        -release)
            debug=no
            release=yes
            ;;
        -spec)
            shift
            if [ $# -eq 0 ] ; then
                echo "-prefix needs an argument" 2>&1
                usage
            fi
            SPEC="-spec $1"
            ;;
        *)
            usage "$1"
            ;;
    esac
    shift
done

find . -name debug -o -name release -o -name Makefile\* | xargs rm -rf

if [ -f src/src.pro ] ; then
    rm -rf lib bin
fi

default_prefix=/usr/local/KDAB/$Product-$VERSION
if [ -z "$prefix" ] ; then
    prefix="$default_prefix"
fi

echo -n > ".qmake.cache"
(
    echo "VERSION=$VERSION"
    echo "CONFIG += ${product}_target"

    if [ "$debug" = "yes" ]; then
      echo "CONFIG -= release"
      echo "CONFIG += debug"
      echo "CONFIG -= debug_and_release"
    fi

    if [ "$release" = "yes" ]; then
      echo "CONFIG += release"
      echo "CONFIG -= debug"
      echo "CONFIG -= debug_and_release"
    fi

    [ "$hide_symbols" = "yes" ] &&  echo "CONFIG += hide_symbols"
    [ "$unittests" = "yes" ] && echo "CONFIG += unittests"

    if [ "$shared" = "yes" ]; then
      echo "CONFIG -= static"
      echo "CONFIG -= staticlib"
      echo "CONFIG += shared"
    else
      echo "CONFIG += static"
      echo "CONFIG += staticlib"
      echo "CONFIG -= shared"
    fi

    if [ -d "$QTDIR/include/Qt/private" ] ; then
	echo "CONFIG += have_private_qt_headers"
	echo "INCLUDEPATH += $QTDIR/include/Qt/private"
    #else
        #echo "QTDIR must point to an installation that has private headers installed."
        #echo "Some features will not be available."    
    fi
[ "$INSTALLATION_SUPPORTED" = "true" ] && echo "${PRODUCT}_INSTALL_PREFIX = $prefix"

) >> ".qmake.cache"

cat <<EOF 1>&2
$ProductSpace v$VERSION configuration:
EOF

if [ "$INSTALLATION_SUPPORTED" = "true" ]; then
cat <<EOF 1>&2
  Install Prefix.............: $prefix
    (default: $default_prefix)
EOF
fi

cat <<EOF 1>&2
  Debug......................: $debug (default: no)
  Release....................: $release (default: yes)
EOF
if [ "$STATIC_BUILD_SUPPORTED" = "true" ]; then
  cat <<EOF 1>&2
  Shared build...............: $shared (default: yes)
EOF
fi
if [ "$SPEC" != "" ]; then
  cat <<EOF 1>&2
  Spec.......................: ${SPEC#-spec }
EOF
fi
cat <<EOF 1>&2
  Compiled-In Unit Tests.....: $unittests (default: no)
  Restricted symbol export
    (shared build only)......: $hide_symbols (default: yes)

EOF

# Make a copy so that each run of qmake on $product.pro starts clean
cp -f .qmake.cache .confqmake.cache

$QTDIR/bin/qmake ${SPEC} $product.pro -recursive "${PRODUCT}_BASE=`pwd`" || die "qmake failed"

if [ "$INSTALLATION_SUPPORTED" = "true" ]; then
  echo "Ok, now run make, then make install to install into $prefix"
else
  echo "Ok, now run make to build the framework."
fi 
"""

CONFIGURE_BAT_IN = """\
@echo off
rem This file was generated automatically.
rem Please edit buildsystem/autotools/autogen.py rather than this file.

set PRODUCT_CAP=@PRODUCT_UPPERCASE@
set product_low=@PRODUCT_LOWERCASE@
set Product_mix=@PRODUCT_MIXEDCASE@
set Product_Space="@PRODUCT_MIXEDCASE_SPACED@"

set VERSION=@VERSION@

set INSTALLATION_SUPPORTED=@INSTALLATION_SUPPORTED@
set STATIC_BUILD_SUPPORTED=@STATIC_BUILD_SUPPORTED@

set PACKSCRIPTS_DIR=../admin/packscripts

set shared=yes
set debug=no
set release=no
set prefix=
set unittests=no

if exist %PACKSCRIPTS_DIR% (
    set unittests=yes
    goto :CheckLicenseComplete
)

if exist .license.accepted goto :CheckLicenseComplete

set license_file=

if exist LICENSE.GPL.txt (
    if exist LICENSE.US.txt (
        if exist LICENSE.txt (
            echo.
            echo Please choose your license.
            echo.
            echo Type 1 for the GNU General Public License ^(GPL^).
            echo Type 2 for the %Product_Space% Commercial License for USA/Canada.
            echo Type 3 for the %Product_Space% Commercial License for anywhere outside USA/Canada.
            echo Anything else cancels.
            echo.
            set /p license=Select:
	)
    ) else (
        license=1
    )
) else (
    if exist LICENSE.US.txt (
        license=2
    ) else (
        if exist LICENSE.txt (
            license=3
        ) else (
            echo "Couldn't find license file, aborting"
            exit /B 1
        )
    )
)

if "%license%" == "1" (
    set license_name="GNU General Public License (GPL)"
    set license_file=LICENSE.GPL.txt
	goto :CheckLicense
) else (
    if "%license%" == "2" (
        set license_name="%Product_Space% USA/Canada Commercial License"
        set license_file=LICENSE.US.txt
        goto :CheckLicense
    ) else (
        if "%license%" == "3" (
            set license_name="%Product_Space% Commercial License"
            set license_file=LICENSE.txt
            goto :CheckLicense
        ) else (
            exit /B 1
        )
    )
)

:CheckLicense
echo.
echo License Agreement
echo.
echo You are licensed to use this software under the terms of
echo the %license_name%.
echo.
echo Type '?' to view the %license_name%.
echo Type 'yes' to accept this license offer.
echo Type 'no' to decline this license offer.
echo.
set /p answer=Do you accept the terms of this license?

if "%answer%" == "no" goto :CheckLicenseFailed
if "%answer%" == "yes" (
    echo. > .license.accepted
    goto :CheckLicenseComplete
)
if "%answer%" == "?" more %license_file%
goto :CheckLicense

:CheckLicenseFailed
echo You are not licensed to use this software.
exit /B 1

:CheckLicenseComplete

if "%QTDIR%" == "" (
  rem This is the batch equivalent of QTDIR=`qmake -query QT_INSTALL_PREFIX`...
  for /f "tokens=*" %%V in ('qmake -query QT_INSTALL_PREFIX') do set QTDIR=%%V
)

if "%QTDIR%" == "" (
  echo You need to set QTDIR or add qmake to the PATH
  exit /B 1
)

echo Qt found: %QTDIR%

del /Q /S Makefile* 2> NUL
del /Q /S debug 2> NUL
del /Q /S release 2> NUL
if exist src\src.pro (
    del /Q lib 2> NUL
    del /Q bin 2> NUL
)
del .qmake.cache 2> NUL

echo. > .qmake.cache

:Options
if "%1" == ""          goto :EndOfOptions

if "%1" == "-prefix"   goto :Prefix
if "%1" == "/prefix"   goto :Prefix

if "%1" == "-override-version"  goto :OverrideVersion
if "%1" == "/override-version"  goto :OverrideVersion

if "%1" == "-unittests"    goto :Unittests
if "%1" == "/unittests"    goto :Unittests

if "%1" == "-no-unittests" goto :NoUnittests
if "%1" == "/no-unittests" goto :NoUnittests

if "%1" == "-shared"   goto :Shared
if "%1" == "/shared"   goto :Shared

if "%1" == "-static"   goto :Static
if "%1" == "/static"   goto :Static

if "%1" == "-release"  goto :Release
if "%1" == "/release"  goto :Release

if "%1" == "-debug"    goto :Debug
if "%1" == "/debug"    goto :Debug

if "%1" == "-help"     goto :Help
if "%1" == "/help"     goto :Help
if "%1" == "--help"    goto :Help
if "%1" == "/?"        goto :Help

echo Unknown option: %1
goto :usage

:OptionWithArg
shift
:OptionNoArg
shift
goto :Options

:Prefix
    if "%INSTALLATION_SUPPORTED%" == "true" (
      set prefix="%2"
      goto :OptionWithArg
    ) else (
      echo Installation not supported, -prefix option ignored
      goto :OptionWithArg
rem   goto :usage
    )
:OverrideVersion
    set VERSION=%2
    goto :OptionWithArg
:Unittests
    set unittests=yes
    goto :OptionNoArg
:NoUnittests
    set unittests=no
    goto :OptionNoArg
:Shared
    set shared=yes
    goto :OptionNoArg
:Static
if "%STATIC_BUILD_SUPPORTED%" == "true" (
    set shared=no
    goto :OptionNoArg
) else (
  echo Static build not supported, -static option not allowed
  goto :usage
)
:Release
    set release=yes
    goto :OptionNoArg
:Debug
    set debug=yes
    goto :OptionNoArg
:Help
    goto :usage

:EndOfOptions

if "%release%" == "yes" (
    if "%debug%" == "yes" (
        echo CONFIG += debug_and_release build_all >> .qmake.cache
	set release="yes (combined)"
	set debug="yes (combined)"
    ) else (
        echo CONFIG += release >> .qmake.cache
        echo CONFIG -= debug >> .qmake.cache
	echo CONFIG -= debug_and_release >> .qmake.cache
    )
) else (
    if "%debug%" == "yes" (
        echo CONFIG -= release >> .qmake.cache
	echo CONFIG += debug >> .qmake.cache
	echo CONFIG -= debug_and_release >> .qmake.cache
    ) else (
	echo CONFIG += debug_and_release build_all >> .qmake.cache
	set release="yes (combined)"
	set debug="yes (combined)"
    )
)

if "%shared%" == "yes" (
    echo CONFIG += shared >> .qmake.cache
) else (
    echo CONFIG += static >> .qmake.cache
    rem This is needed too, when Qt is static, otherwise it sets -DQT_DLL and linking fails.
    echo CONFIG += qt_static >> .qmake.cache
)

if "%unittests%" == "yes" (
    echo CONFIG += unittests >> .qmake.cache
)

set default_prefix=C:\KDAB\%Product_mix%-%VERSION%

if "%prefix%" == "" (
    set prefix="%default_prefix%"
)
echo %PRODUCT_CAP%_INSTALL_PREFIX = %prefix% >> .qmake.cache


echo VERSION=%VERSION% >> .qmake.cache
echo CONFIG += %product_low%_target >> .qmake.cache

if exist "%QTDIR%\include\Qt\private" (
    echo CONFIG += have_private_qt_headers >> .qmake.cache
    echo INCLUDEPATH += %QTDIR%/include/Qt/private >> .qmake.cache
) else (
    rem echo QTDIR must point to an installation that has private headers installed.
    rem echo Some features will not be available.
)

echo %Product_mix% v%VERSION% configuration:
echo.
echo   Debug...................: %debug% (default: combined)
echo   Release.................: %release% (default: combined)
if "%STATIC_BUILD_SUPPORTED%" == "true" (
  echo   Shared build............: %shared% (default: yes)
)
echo   Compiled-In Unit Tests..: %unittests% (default: no)
echo.

rem Make a copy so that each run of qmake on $product.pro starts clean
copy .qmake.cache .confqmake.cache

%QTDIR%\bin\qmake %product_low%.pro -recursive "%PRODUCT_CAP%_BASE=%CD%"

if errorlevel 1 (
    echo qmake failed
    goto :CleanEnd
)

echo Ok, now run nmake (for Visual Studio) or mingw32-make (for mingw) to build the framework.
goto :end

:usage
IF "%1" NEQ "" echo %0: unknown option "%1"
echo usage: %0 [options]
echo where options include:
if "%INSTALLATION_SUPPORTED%" == "true" (
  echo.
  echo   -prefix <dir> 
  echo       set installation prefix to <dir>, used by make install
)
echo.
echo   -release / -debug
echo       build in debug/release mode
if "%STATIC_BUILD_SUPPORTED%" == "true" (
  echo.
  echo   -static / -shared
  echo       build static/shared libraries
)
echo.
echo   -unittests / -no-unittests
echo       enable/disable compiled-in unittests
echo.

:CleanEnd
del .qmake.cache

:end
"""


class Action( object ):

	def __init__( self, name = None ):
		pass

	def run( self ):
		raise NotImplementedError()

def data_dir():
	return os.path.dirname( __file__ )


class ConfigureScriptGenerator( Action ):

	def __init__( self, project, path, version, install = True, static = True, name = None ):
		Action.__init__( self, name )
		self.__project = project
		self.__install = install
		self.__static = static
		self.__path = path
		self.__version = version
		self.__winTemplate = os.path.abspath( data_dir() + "/configure.bat.in" )
		self.__unixTemplate = os.path.abspath( data_dir() + "/configure.sh.in" )

	def __del__( self ):
		pass

	def run( self ):
		self.__generate()
		return 0

	def __replaceValues( self, value ):
		mixedname = self.__project
		mixedname = mixedname.replace( "KD", "KD " )
		value = value.replace( "@VERSION@", self.__version )
		value = value.replace( "@PRODUCT_UPPERCASE@", self.__project.upper() )
		value = value.replace( "@PRODUCT_LOWERCASE@", self.__project.lower() )
		value = value.replace( "@PRODUCT_MIXEDCASE@", self.__project )
		value = value.replace( "@PRODUCT_MIXEDCASE_SPACED@", mixedname )
		if ( self.__install ):
			value = value.replace( "@INSTALLATION_SUPPORTED@", "true" )
		else:
			value = value.replace( "@INSTALLATION_SUPPORTED@", "false" )
		if ( self.__static ):
			value = value.replace( "@STATIC_BUILD_SUPPORTED@", "true" )
		else:
			value = value.replace( "@STATIC_BUILD_SUPPORTED@", "false" )
		return value

	def __generate( self ):
		self.__generateFile( self.__unixTemplate, os.path.abspath( self.__path + "/configure.sh" ), "unix" )
		self.__generateFile( self.__winTemplate, os.path.abspath( self.__path + "/configure.bat" ), "win32" )

	def __generateFile( self, templateFile, outputFile, platformString ):
		if platformString == "win32":
			lineSep = "\r\n"
		else:
			lineSep = "\n"

		fOutput = open( outputFile, "wb" )
		for line in ( CONFIGURE_BAT_IN.splitlines() if platformString == "win32" else CONFIGURE_SH_IN.splitlines() ):
			fOutput.write( self.__replaceValues( line.rstrip() ) + lineSep )
		fOutput.close()


def print_stderr( message ):
	print( message, file = sys.stderr )

def my_copyfile( src, dest ):
	#print_stderr( "Copying file: {0} -> {1}".format( src, dest ) )
	copyfile( src, dest )

class ForwardHeaderGenerator( Action ):

	def __init__( self, copy, path, includepath, srcpath, project, subprojects, prefix, prefixed = False, name = None ):
		Action.__init__( self, name )
		self.copy = copy
		self.path = path
		self.includepath = includepath
		self.srcpath = srcpath
		self.project = project
		self.subprojects = subprojects
		self.prefix = prefix
		self.prefixed = prefixed
		self.__projectFile = ""

	def run( self ):
		self.createProject()
		return 0

	def getLogDescription( self ):
		return 'Generating forward headers'

	def _checkFileName( self, filename ):
		if ( filename.endswith( ".h" ) ):
			if filename.startswith( "moc_" ):
				return False
			if ( filename.startswith( "ui_" ) ):
				return False
			if ( filename.startswith( "qrc_" ) ):
				return False;
			if ( filename.endswith( "_p.h" ) ):
				return False
			return True
		else:
			return False

	def _suggestedHeaderNames( self, project, header ):
		regex = re.compile( "(?:class\s+[{0}|{1}][_0-9A-Z]*_EXPORT|MAKEINCLUDES_EXPORT)\s+([a-zA-Z_][A-Za-z0-9_]*)".format( project.upper(), self.project.upper() ) )
		regex2 = re.compile( "(?:class\s+MAKEINCLUDES_EXPORT)\s+([a-zA-Z_][A-Za-z0-9_]*)" )
		regex3 = re.compile( "(?:\\\\file)\s+([a-zA-Z_][A-Za-z0-9_]*)" )

		f = open( header, "r" )
		classNames = set()

		for line in f.readlines():
			line = line.rstrip()
			line = line.lstrip()

			className = None
			noPrefix = False
			if ( regex.match( line ) ):
				className = regex.match( line ).groups()[0]
				noPrefix = False
			else:
				if regex2.match( line ):
					className = regex2.match( line ).groups()[0]
					noPrefix = False
				else:
					if ( None != regex3.search( line ) ):
						className = regex3.search( line ).groups()[0]
						noPrefix = True

			if not className:
				continue

			if self.prefixed and not noPrefix:
				className = project + className

			classNames.add( className )

		f.close()

		return classNames

	def _createForwardHeader( self, header, projectFile, project ):
		classNames = self._suggestedHeaderNames( project, header )
		path = os.path.dirname( header )

		print_stderr( "Parsing file: {0} (Project: {1})".format( header, project ) )
		for classname in classNames:
			if ( self.prefixed ):
				localPath = self.includepath + "/" + os.path.basename( header )
				my_copyfile( header, localPath )
				self.__projectFile.write( os.path.basename( header ) + " \\" + os.linesep )
				self.__projectFile.write( classname + " \\" + os.linesep )
				fHeaderName = os.path.abspath( self.includepath + "/" + classname )
				newHeader = open( fHeaderName, "wb" )
				input = "#include \"REPLACE\""
				input = input.replace( "REPLACE", os.path.basename( header ) )
				newHeader.write( input + os.linesep )
				newHeader.close()

			fHeaderName = os.path.abspath( path + "/" + classname )
			projectFile.write( os.path.basename( header ) + " \\" + os.linesep )
			projectFile.write( classname + " \\" + os.linesep )
			newHeader = open( fHeaderName, "wb" )
			input = "#include \"REPLACE\""
			input = input.replace( "REPLACE", os.path.basename( header ) )
			newHeader.write( input + os.linesep )
			newHeader.close()

			print_stderr( "  Forward header generated for {0}".format( classname ) )

		if len( classNames ) == 0:
			print_stderr( "  No input classes found. No forward header generated." )

			if ( self.prefixed ):
				localPath = self.includepath + "/" + os.path.basename( header )
				my_copyfile( header, localPath )
				self.__projectFile.write( os.path.basename( header ) + " \\" + os.linesep )

			basename = os.path.basename( header )
			basename = basename[ 0: basename.rfind( '.h' ) ]
			fHeaderName = os.path.abspath( self.includepath + "/" + basename )
			newHeader = open( fHeaderName, "wb" )
			input = "#include \"REPLACE\""
			input = input.replace( "REPLACE", os.path.basename( header ) )
			newHeader.write( input + os.linesep )
			newHeader.close()

			fHeaderNameProjectDir = os.path.dirname( os.path.abspath( header ) ) + "/" + basename;
			newHeader = open( fHeaderNameProjectDir, "wb" )
			input = "#include \"../REPLACE\""
			input = input.replace( "REPLACE", os.path.basename( header ) )
			newHeader.write( input + os.linesep )
			newHeader.close()

			projectFile.write( os.path.basename( fHeaderName ) + " \\" + os.linesep )
			self.__projectFile.write( os.path.basename( fHeaderName ) + " \\" + os.linesep )

	def createProject( self ):
		if ( not os.path.exists( self.path ) ):
			errStr = Template( "Error, the directory $DIR does not exist!" )
			errStr = errStr.substitute( DIR = self.path )
			raise BaseException( errStr )
		if ( os.path.exists( self.includepath ) ):
			rmtree( self.includepath )
		os.mkdir( self.includepath )
		profilename = os.path.abspath( self.includepath ) + "/" + self.project + ".pro"
		projectFile = open( profilename, "wb" )
		self.__projectFile = projectFile
		lines = []
		lines.append( "TEMPLATE = subdirs" + os.linesep )
		lines.append( "SUBDIRS = " )
		for subProject in self.subprojects:
			line = subProject
			if ( subProject != self.subprojects[ -1 ] ):
				line += " \\"
			line += os.linesep

			lines.append( line )

		projectFile.writelines( lines )
		projectFile.write( os.linesep )

		projectFile.write( "INSTALL_HEADERS.files = " )

		for subProject in self.subprojects:
			self._createSubproject( subProject )

		self._copyHeaders( self.srcpath, self.includepath, projectFile, self.project, self.prefixed )
		installPath = "{0}/include".format( self.prefix )
		self._projectFile_finalize( projectFile, installPath )
		projectFile.close()

	def _createSubproject( self, project ):
		inclPath = os.path.abspath( self.includepath + "/" + project )
		srcPath = os.path.abspath( self.srcpath + "/" + project )
		os.mkdir( inclPath )
		profilename = os.path.abspath( self.includepath ) + "/" + project + "/" + project + ".pro"
		projectFile = open( profilename, "wb" )
		projectFile.write( "TEMPLATE = subdirs" + os.linesep )
		projectFile.write( "INSTALL_HEADERS.files = " )
		self._copyHeaders( srcPath, inclPath, projectFile, project, self.prefixed )
		installPath = "{0}/include/{1}".format( self.prefix, project )
		self._projectFile_finalize( projectFile, installPath )
		projectFile.close()

	def _projectFile_finalize( self, projectFile, installPath ):
		projectFile.write( os.linesep )
		projectFile.write( "message( $$INSTALL_HEADERS.path )" + os.linesep )
		projectFile.write( "INSTALL_HEADERS.path = {0}".format( installPath ) + os.linesep )
		projectFile.write( "message( $$INSTALL_HEADERS.path )" + os.linesep )
		projectFile.write( "INSTALLS += INSTALL_HEADERS" + os.linesep )

	def _copyHeaders( self, srcDir, destDir, projectFile, project, prefixed = False ):
		rootDir = srcDir == self.srcpath
		dir = os.listdir( srcDir )
		for filename in dir:
			if ( rootDir ):
				if ( filename in self.subprojects ):
					continue
			file = os.path.abspath( srcDir + "/" + filename )
			if ( not os.path.isdir( file ) ):
				destfile = os.path.abspath( destDir + "/" + filename )
				srcfile = os.path.abspath( srcDir + "/" + filename )
				if ( self._checkFileName( filename ) ):
					my_copyfile( srcfile, destfile )
					self._createForwardHeader( destfile, projectFile, project )
			else:
				continue


# SCRIPTS

BUILD_DIRECTORY = os.getcwd()
SOURCE_DIRECTORY = os.path.dirname( os.path.abspath( __file__ ) )

def kdreports_autogen():
	PROJECT = "KDReports"
	VERSION = "1.3.0"
	SUBPROJECTS = "KDReports".split( " " )
	PREFIX = "$$INSTALL_PREFIX/KDReports"

	configureScriptGenerator = ConfigureScriptGenerator( project = PROJECT, path = BUILD_DIRECTORY, version = VERSION )
	assert( configureScriptGenerator.run() == 0 )

	includePath = os.path.join( SOURCE_DIRECTORY, "include" )
	srcPath = os.path.join( SOURCE_DIRECTORY, "src" )
	forwardHeaderGenerator = ForwardHeaderGenerator( 
			copy = True, path = SOURCE_DIRECTORY, includepath = includePath, srcpath = srcPath,
			project = PROJECT, subprojects = SUBPROJECTS, prefix = PREFIX, prefixed = True
	 )
	assert( forwardHeaderGenerator.run() == 0 )

def kdchart_autogen():
	PROJECT = "KDChart"
	VERSION = "2.4.0"
	SUBPROJECTS = "KDChart KDGantt".split( " " )
	PREFIX = "$$INSTALL_PREFIX/KDChart"

	configureScriptGenerator = ConfigureScriptGenerator( project = PROJECT, path = BUILD_DIRECTORY, version = VERSION )
	assert( configureScriptGenerator.run() == 0 )

	includePath = os.path.join( SOURCE_DIRECTORY, "include" )
	srcPath = os.path.join( SOURCE_DIRECTORY, "src" )
	forwardHeaderGenerator = ForwardHeaderGenerator( 
			copy = True, path = SOURCE_DIRECTORY, includepath = includePath, srcpath = srcPath,
			project = "KDChart", subprojects = SUBPROJECTS, prefix = PREFIX, prefixed = True
	 )
	assert( forwardHeaderGenerator.run() == 0 )

def kdsoap_autogen():
	PROJECT = "KDSoap"
	VERSION = "1.1.0"
	SUBPROJECTS = "KDSoapClient KDSoapServer".split( " " )
	PREFIX = "$$INSTALL_PREFIX/{0}".format( PROJECT )

	configureScriptGenerator = ConfigureScriptGenerator( project = PROJECT, path = BUILD_DIRECTORY, version = VERSION )
	assert( configureScriptGenerator.run() == 0 )

	includePath = os.path.join( SOURCE_DIRECTORY, "include" )
	srcPath = os.path.join( SOURCE_DIRECTORY, "src" )
	forwardHeaderGenerator = ForwardHeaderGenerator( 
			copy = True, path = SOURCE_DIRECTORY, includepath = includePath, srcpath = srcPath,
			project = PROJECT, subprojects = SUBPROJECTS, prefix = PREFIX, prefixed = True
	 )
	assert( forwardHeaderGenerator.run() == 0 )

def call_handler( svnInfoMessage ):
	"""\return True if handler found, else False"""

	if "products/kdsoap" in out[0]:
		kdsoap_autogen()
	elif "products/kdchart" in out[0]:
		kdchart_autogen()
	elif "products/kdreports" in out[0]:
		kdreports_autogen()
	else:
		return False

	return True

if __name__ == "__main__":
	# check repository, call corresponding autogen script for our products
	# see "# SCRIPTS" section

	# check repository URL
	p = Popen( ["svn", "info"], stdout = PIPE, stderr = PIPE )
	out = p.communicate()

	# call handler, check return code
	isOk = call_handler( out[0] )
	if not isOk:
		print_stderr( "Warning. No handler for this repository!" )
		sys.exit( 1 )

	# give feedback
	print( "Finished.", file = sys.stderr )
	sys.exit( 0 )
