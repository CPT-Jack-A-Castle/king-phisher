#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  king_phisher/sphinxext/database.py
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the project nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import re

from . import _exttools

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import ObjType
from sphinx.util import docfields

NAMESPACE = 'db'

class DescDatabaseFieldArgument(_exttools.ArgumentBase):
	"""Node for an argument wrapper"""

class DescDatabaseFieldArgumentList(_exttools.ArgumentListBase):
	"""Node for a general argument list."""

class DatabaseTable(_exttools.GenericObjectBase):
	label = 'Database table'
	attribute = 'table'
	xref_prefix = NAMESPACE

class DatabaseField(ObjectDescription):
	doc_field_types = [
		docfields.TypedField(
			'foreignkey',
			label='Foreign Key',
			names=('fkey', 'foreignkey'),
			can_collapse=True
		),
		docfields.Field(
			'nullable',
			has_arg=False,
			label='Nullable',
			names=('nullable',),
		),
		docfields.Field(
			'type',
			has_arg=False,
			label='Data Type',
			names=('type',),
		),
		docfields.TypedField(
			'parameter',
			label='Parameters',
			names=('param', 'parameter'),
			typenames=('paramtype', 'type'),
			typerolename='class',
			can_collapse=True,
		),
		docfields.Field(
			'primarykey',
			has_arg=False,
			label='Primary Key',
			names=('pkey', 'primarykey'),
		)
	]
	def add_target_and_index(self, name, sig, signode):
		targetname = 'db:%s-%s' % (self.objtype, name)
		signode['ids'].append(targetname)
		self.state.document.note_explicit_target(signode)
		self.env.domaindata[self.domain]['objects'][self.objtype, name] = self.env.docname, targetname

	def handle_signature(self, sig, signode):
		match = re.match(r'(?P<name>[a-z0-9_]+)(\((?P<arguments>[a-z_0-9]+(, +[a-z_0-9]+)*)\))?', sig)
		field_name = match.group('name')
		if 'db:table' in self.env.ref_context:
			full_name = self.env.ref_context['db:table'] + '.' + field_name
		else:
			full_name = field_name
		signode += addnodes.desc_name(field_name, field_name)
		arguments = match.group('arguments')
		if arguments:
			plist = DescDatabaseFieldArgumentList()
			arguments = arguments.split(',')
			for pos, arg in enumerate(arguments):
				arg = arg.strip()
				if pos < len(arguments) - 1:
					arg += ','
				x = DescDatabaseFieldArgument()
				x += addnodes.desc_parameter(arg, arg)
				plist += x
			signode += plist
		return full_name

class DatabaseXRefRole(_exttools.XRefRoleBase):
	attribute = 'table'
	xref_prefix = NAMESPACE

class DatabaseDomain(_exttools.DomainBase):
	name = NAMESPACE
	label = 'Database'
	directives = {
		'field': DatabaseField,
		'table': DatabaseTable,
	}
	object_types = {
		'field': ObjType('Database Field', 'fld'),
		'table': ObjType('Database Object', 'tbl'),
	}
	roles = {
		'fld': DatabaseXRefRole(),
		'tbl': DatabaseXRefRole(),
	}

def setup(app):
	_exttools.add_app_node_arguments(app, DescDatabaseFieldArgument, DescDatabaseFieldArgumentList)
	app.add_domain(DatabaseDomain)
