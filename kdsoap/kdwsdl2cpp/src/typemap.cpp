/*
    This file is part of KDE.

    Copyright (c) 2005 Tobias Koenig <tokoe@kde.org>

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public License
    along with this library; see the file COPYING.LIB.  If not, write to
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
    Boston, MA 02110-1301, USA.
*/

#include <common/nsmanager.h>

#include <QDebug>
#include "typemap.h"

using namespace KWSDL;

static QString adaptLocalTypeName( const QString &str )
{
  QString result( str );
  result[ 0 ] = result[ 0 ].toUpper();

  if ( result.endsWith( "[]" ) )
    result.truncate( result.length() - 2 );

  return result;
}

TypeMap::TypeMap()
  : mNSManager( 0 )
{
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "any";
    entry.localType = "QString";
    entry.headers << "QString";
    entry.headerIncludes << "QString";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "anyURI";
    entry.localType = "QString";
    entry.headers << "QString";
    entry.headerIncludes << "QString";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "base64Binary";
    entry.localType = "QByteArray";
    entry.headers << "QByteArray";
    entry.headerIncludes << "QByteArray";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "binary";
    entry.localType = "QByteArray";
    entry.headers << "QByteArray";
    entry.headerIncludes << "QByteArray";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "boolean";
    entry.localType = "bool";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "byte";
    entry.localType = "char";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "date";
    entry.localType = "QDate";
    entry.headers << "QDate";
    entry.headerIncludes << "QDate";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "dateTime";
    entry.localType = "QDateTime";
    entry.headers << "QDateTime";
    entry.headerIncludes << "QDateTime";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "decimal";
    entry.localType = "float";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "double";
    entry.localType = "double";
    mTypeMap.append( entry );
  }
  { // TODO: add duration class
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "duration";
    entry.localType = "QString";
    entry.headers << "QString";
    entry.headerIncludes << "QString";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "float";
    entry.localType = "float";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "integer";
    entry.localType = "int";
    mTypeMap.append( entry );

    entry.typeName = "int";
    mTypeMap.append( entry );

    entry.typeName = "nonPositiveInteger";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "language";
    entry.localType = "QString";
    entry.headers << "QString";
    entry.headerIncludes << "QString";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "short";
    entry.localType = "short";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "string";
    entry.localType = "QString";
    entry.headers << "QString";
    entry.headerIncludes << "QString";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "time";
    entry.localType = "QTime";
    entry.headers << "QTime";
    entry.headerIncludes << "QTime";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "unsignedByte";
    entry.localType = "unsigned char";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "unsignedLong";
    entry.localType = "unsigned long";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "positiveInteger";
    entry.localType = "unsigned int";
    mTypeMap.append( entry );

    entry.typeName = "nonNegativeInteger";
    mTypeMap.append( entry );

    entry.typeName = "unsignedInt";
    mTypeMap.append( entry );
  }
  {
    Entry entry;
    entry.basicType = true;
    entry.buildinType = true;
    entry.nameSpace = XMLSchemaURI;
    entry.typeName = "token";
    entry.headers << "QString";
    entry.localType = "QString";
    mTypeMap.append( entry );
   }
}

TypeMap::~TypeMap()
{
}

void TypeMap::setNSManager( NSManager *manager )
{
  mNSManager = manager;
}


QList<TypeMap::Entry>::ConstIterator TypeMap::typeEntry( const QName &typeName ) const
{
    QList<Entry>::ConstIterator it;
    for ( it = mTypeMap.constBegin(); it != mTypeMap.constEnd(); ++it ) {
      if ( (*it).typeName == typeName.localName() && (*it).nameSpace == typeName.nameSpace() )
        break;
    }
    return it;
}

bool TypeMap::isBasicType( const QName &typeName )
{
  QList<Entry>::ConstIterator it = typeEntry( typeName );
  return it != mTypeMap.constEnd() ? (*it).basicType : false;
}

bool TypeMap::isBuiltinType( const QName &typeName )
{
  QList<Entry>::ConstIterator it = typeEntry( typeName );
  return it != mTypeMap.constEnd() ? (*it).buildinType : false;
}

QString TypeMap::localType( const QName &typeName )
{
  QList<Entry>::ConstIterator it = typeEntry( typeName );
  if ( it == mTypeMap.constEnd() ) {
      qDebug() << "basic type not found:" << typeName.qname();
      return QString();
  }
  return (*it).localType;
}

QStringList TypeMap::headers( const QName &typeName )
{
  QList<Entry>::ConstIterator it = typeEntry( typeName );
  return it != mTypeMap.constEnd() ? (*it).headers : QStringList();
}

QStringList TypeMap::forwardDeclarations( const QName &typeName )
{
  QList<Entry>::ConstIterator it = typeEntry( typeName );
  return it != mTypeMap.constEnd() ? (*it).forwardDeclarations : QStringList();
}

QStringList TypeMap::headerIncludes( const QName &typeName )
{
  QList<Entry>::ConstIterator it = typeEntry( typeName );
  return it != mTypeMap.constEnd() ? (*it).headerIncludes : QStringList();
}



QString TypeMap::localTypeForAttribute( const QName &typeName )
{
  QList<Entry>::ConstIterator it;
  for ( it = mAttributeMap.constBegin(); it != mAttributeMap.constEnd(); ++it ) {
    if ( (*it).typeName == typeName.localName() && (*it).nameSpace == typeName.nameSpace() )
      return (*it).localType;
  }

  return QString();
}

QStringList TypeMap::headersForAttribute( const QName &typeName )
{
  QList<Entry>::ConstIterator it;
  for ( it = mAttributeMap.constBegin(); it != mAttributeMap.constEnd(); ++it ) {
    if ( (*it).typeName == typeName.localName() && (*it).nameSpace == typeName.nameSpace() )
      return (*it).headers;
  }

  return QStringList();
}

QStringList TypeMap::forwardDeclarationsForAttribute( const QName &typeName )
{
  QList<Entry>::ConstIterator it;
  for ( it = mAttributeMap.constBegin(); it != mAttributeMap.constEnd(); ++it ) {
    if ( (*it).typeName == typeName.localName() && (*it).nameSpace == typeName.nameSpace() )
      return (*it).forwardDeclarations;
  }

  return QStringList();
}

QList<TypeMap::Entry>::ConstIterator TypeMap::elementEntry( const QName &typeName ) const
{
  QList<Entry>::ConstIterator it;
  for ( it = mElementMap.constBegin(); it != mElementMap.constEnd(); ++it ) {
    if ( (*it).typeName == typeName.localName() && (*it).nameSpace == typeName.nameSpace() )
      break;
  }
  return it;
}

QString TypeMap::localTypeForElement( const QName &typeName )
{
  QList<Entry>::ConstIterator it = elementEntry( typeName );
  if ( it != mElementMap.constEnd() ) {
      return (*it).localType;
  }

  qDebug() << "TypeMap::localTypeForElement: unknown type" << typeName.qname();
  return QString();
}

QStringList TypeMap::headersForElement( const QName &typeName )
{
  QList<Entry>::ConstIterator it = elementEntry( typeName );
  return it != mElementMap.constEnd() ? (*it).headers : QStringList();
}

QStringList TypeMap::forwardDeclarationsForElement( const QName &typeName )
{
  QList<Entry>::ConstIterator it = elementEntry( typeName );
  return it != mElementMap.constEnd() ? (*it).forwardDeclarations : QStringList();
}

void TypeMap::addSchemaTypes( const XSD::Types &types )
{
  Q_ASSERT( mNSManager );

  XSD::SimpleType::List simpleTypes = types.simpleTypes();
  XSD::SimpleType::List::ConstIterator simpleIt;
  for ( simpleIt = simpleTypes.constBegin(); simpleIt != simpleTypes.constEnd(); ++simpleIt ) {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = false;
    entry.nameSpace = (*simpleIt).nameSpace();
    entry.typeName = (*simpleIt).name();
    entry.localType = mNSManager->prefix( entry.nameSpace ).toUpper() + "__" + adaptLocalTypeName( (*simpleIt).name() );
    entry.headers << (*simpleIt).name().toLower() + ".h";
    entry.forwardDeclarations << entry.localType;

    mTypeMap.append( entry );
  }

  XSD::ComplexType::List complexTypes = types.complexTypes();
  XSD::ComplexType::List::ConstIterator complexIt;
  for ( complexIt = complexTypes.constBegin(); complexIt != complexTypes.constEnd(); ++complexIt ) {
    if (!(*complexIt).isEmpty()) {
      Entry entry;
      entry.basicType = false;
      entry.buildinType = false;
      entry.nameSpace = (*complexIt).nameSpace();
      entry.typeName = (*complexIt).name();
      entry.localType = mNSManager->prefix( entry.nameSpace ).toUpper() + "__" + adaptLocalTypeName( (*complexIt).name() );
      entry.headers << (*complexIt).name().toLower() + ".h";
      entry.forwardDeclarations << entry.localType;

      mTypeMap.append( entry );
    }
  }

  XSD::Attribute::List attributes = types.attributes();
  XSD::Attribute::List::ConstIterator attrIt;
  for ( attrIt = attributes.constBegin(); attrIt != attributes.constEnd(); ++attrIt ) {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = false;
    entry.nameSpace = (*attrIt).nameSpace();
    entry.typeName = (*attrIt).name();
    entry.localType = mNSManager->prefix( entry.nameSpace ).toUpper() + "__" + adaptLocalTypeName( (*attrIt).name() + "Attribute" );
    entry.headers << (*attrIt).name().toLower() + "attribute.h";
    entry.forwardDeclarations << entry.localType;

    mAttributeMap.append( entry );
  }

  XSD::Element::List elements = types.elements();
  XSD::Element::List::ConstIterator elemIt;
  for ( elemIt = elements.constBegin(); elemIt != elements.constEnd(); ++elemIt ) {
    Entry entry;
    entry.basicType = false;
    entry.buildinType = false;
    entry.nameSpace = (*elemIt).nameSpace();
    entry.typeName = (*elemIt).name();
    entry.localType = mNSManager->prefix( entry.nameSpace ).toUpper() + "__" + adaptLocalTypeName( (*elemIt).name() + "Element" );
    entry.headers << (*elemIt).name().toLower() + "element.h";
    entry.forwardDeclarations << entry.localType;

    mElementMap.append( entry );
  }
}

QString TypeMap::inputType( const QString &localType, bool isElement ) const
{
    QString type = localType;
    if ( type.startsWith('Q') || isElement ) {
        type = "const " + type + "&";
    }
    return type;
}

void TypeMap::dump()
{
  qDebug( "--------------------------------" );
  qDebug( "Types:" );
  for ( int i = 0; i < mTypeMap.count(); ++i ) {
    qDebug( "%s\t%s\t%s\t%s\t%s\t%s",
            ( mTypeMap[ i ].basicType ? "basic" : "not basic" ),
              qPrintable( mTypeMap[ i ].nameSpace ),
              qPrintable( mTypeMap[ i ].typeName ),
              qPrintable( mTypeMap[ i ].localType ),
              qPrintable( mTypeMap[ i ].headers.join( "," ) ),
              qPrintable( mTypeMap[ i ].headerIncludes.join( "," ) ) );
  }

  qDebug( "--------------------------------" );
  qDebug( "Attributes:" );
  for ( int i = 0; i < mAttributeMap.count(); ++i ) {
    qDebug( "%s\t%s\t%s\t%s\t%s\t%s",
            ( mAttributeMap[ i ].basicType ? "yes" : "no" ),
              qPrintable( mAttributeMap[ i ].nameSpace ),
              qPrintable( mAttributeMap[ i ].typeName ),
              qPrintable( mAttributeMap[ i ].localType ),
              qPrintable( mAttributeMap[ i ].headers.join( "," ) ),
              qPrintable( mAttributeMap[ i ].headerIncludes.join( "," ) ) );
  }

  qDebug( "--------------------------------" );
  qDebug( "Elements:" );
  for ( int i = 0; i < mElementMap.count(); ++i ) {
    qDebug( "%s\t%s\t%s\t%s\t%s\t%s",
            ( mElementMap[ i ].basicType ? "yes" : "no" ),
              qPrintable( mElementMap[ i ].nameSpace ),
              qPrintable( mElementMap[ i ].typeName ),
              qPrintable( mElementMap[ i ].localType ),
              qPrintable( mElementMap[ i ].headers.join( "," ) ),
              qPrintable( mElementMap[ i ].headerIncludes.join( "," ) ) );
  }
}
