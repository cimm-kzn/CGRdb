# -*- coding: utf-8 -*-
#
#  Copyright 2019-2021 Ramil Nugmanov <nougmanoff@protonmail.com>
#  This file is part of CGRdb.
#
#  CGRdb is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
from io import TextIOWrapper
from pkg_resources import resource_stream


insert_molecule_trigger = '''CREATE TRIGGER cgrdb_insert_molecule_structure
    BEFORE INSERT ON "{schema}"."MoleculeStructure" FOR EACH ROW
    EXECUTE PROCEDURE "{schema}".cgrdb_insert_molecule_structure()'''

after_insert_molecule_trigger = '''CREATE TRIGGER cgrdb_after_insert_molecule_structure
    AFTER INSERT ON "{schema}"."MoleculeStructure" FOR EACH ROW
    EXECUTE PROCEDURE "{schema}".cgrdb_after_insert_molecule_structure()'''

insert_reaction_trigger = '''CREATE TRIGGER cgrdb_insert_reaction
    INSTEAD OF INSERT ON "{schema}"."Reaction" FOR EACH ROW
    EXECUTE PROCEDURE "{schema}".cgrdb_insert_reaction()'''

init_session = '''CREATE OR REPLACE FUNCTION "{schema}".cgrdb_init_session(cfg json)
RETURNS VOID
AS $$
from json import loads

config = loads(cfg)
venv = config.get('environment')
if venv:
    from os.path import join
    activate_this = join(venv, 'bin', 'activate_this.py')
    exec(open(activate_this).read(), {'__file__': activate_this})

from StructureFingerprint import LinearFingerprint

molecule = config.get('molecule', {})
reaction = config.get('reaction', {})
GD['cgrdb_mfp'] = LinearFingerprint(**molecule)
GD['cgrdb_rfp'] = LinearFingerprint(**reaction)
GD['cache_size'] = config.get('cache_size', 256)
GD['index'] = config.get('index')
GD['substructure_limit'] = config.get('substructure_limit') or 10 ** 12

$$ LANGUAGE plpython3u'''.replace('$', '$$')

delete_molecule = '''CREATE OR REPLACE FUNCTION "{schema}".cgrdb_delete_molecule_structure()
RETURNS TRIGGER
AS $$
BEGIN
    DELETE FROM "{schema}"."ReactionIndex" ri WHERE OLD.id = ANY(ri.structures);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql'''.replace('$', '$$')

delete_molecule_trigger = '''CREATE TRIGGER cgrdb_delete_molecule_structure
    AFTER DELETE ON "{schema}"."MoleculeStructure" FOR EACH ROW
    EXECUTE PROCEDURE "{schema}".cgrdb_delete_molecule_structure()'''


def load_sql(file):
    return ''.join(x for x in TextIOWrapper(resource_stream('CGRdb.sql', file))
                   if not x.startswith(('#', '/*', '*/', '\n'))).replace('$', '$$')


insert_molecule = load_sql('insert_molecule.sql')
after_insert_molecule = load_sql('after_insert_molecule.sql')
insert_reaction = load_sql('insert_reaction.sql')

search_structure_molecule = load_sql('find_molecule.sql')
search_structure_reaction = load_sql('find_reaction.sql')
search_substructure_molecule = load_sql('substructure_molecule.sql')
search_substructure_reaction = load_sql('substructure_reaction.sql')
search_similar_molecules = load_sql('similar_molecule.sql')
search_similar_reactions = load_sql('similar_reaction.sql')
search_reactions_by_molecule = load_sql('reaction_by_molecule.sql')
search_mappingless_reaction = load_sql('mappingless_reaction.sql')

merge_molecules = load_sql('merge_molecules.sql')


__all__ = ['init_session', 'insert_molecule', 'after_insert_molecule', 'delete_molecule',
           'insert_molecule_trigger', 'after_insert_molecule_trigger', 'delete_molecule_trigger',
           'insert_reaction', 'insert_reaction_trigger', 'merge_molecules',
           'search_structure_molecule', 'search_structure_reaction',
           'search_substructure_molecule', 'search_substructure_reaction',
           'search_reactions_by_molecule', 'search_mappingless_reaction',
           'search_similar_molecules', 'search_similar_reactions']
