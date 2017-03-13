﻿################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the new BSD license. See the 
# LICENSE file for more information.
#
################################################################################

import re

# Ignore the following line .. this IS the file to edit!
sql = '''
-- THIS FILE IS GENERATED BY build_gazetteer_export.py
--
-- DO NOT MAKE EDITS TO THIS FILE

set search_path=gazetteer,public;

DROP VIEW IF EXISTS name_export CASCADE;
CREATE VIEW name_export AS
with nztm(extent) as 
(
   select ST_SetSRID(
      ST_MakeBox2d( 
         ST_Point(160.0,-50.0),
         ST_Point(180.0,-30.0)
         ), 4167
         )
)
select 
  n.name_id as name_id,
  n.name as name,
  case when sts.category = 'OFFC' then 'Official ' else 'Unofficial ' end ||
      sts.value as status,
  (select value from system_code where code_group='FTYP' and code=f.feat_type) as feat_type,
  f.feat_id as feat_id,
nzgb_ref %NZGZ
land_district @LDIS
  CASE WHEN nztm.extent && f.ref_point THEN 'NZTM' ELSE NULL END as crd_projection,
  CASE WHEN nztm.extent && f.ref_point THEN round(ST_Y(ST_Transform(f.ref_point,2193))::numeric,1) ELSE NULL END as crd_north,
  CASE WHEN nztm.extent && f.ref_point THEN round(ST_X(ST_Transform(f.ref_point,2193))::numeric,1) ELSE NULL END as crd_east,
  CASE WHEN (select value from system_code where code_group='FTYP' and code=f.feat_type) = 'USEA' THEN 'WGS84'
       WHEN ST_Y(f.ref_point) < -60 THEN 'RSRGD2000' 
       ELSE 'NZGD2000'
       END AS crd_datum,
       round(ST_Y(f.ref_point)::numeric,6) AS crd_latitude,
       round(ST_X(f.ref_point)::numeric,6) AS crd_longitude,
info_ref #FLRF
info_origin #HORM
info_note #NNOT
feat_note @FNOT
  f.description as info_description, 
-- info_note (could take from note annotation - original notes mainly populated origin)
maori_name #MRIN
cpa_legislation #CPAL
-- cpa_section 
conservancy #DOCC
doc_cons_unit_no #DOCR
doc_gaz_ref %DOCG
treaty_legislation %TSLG
-- geom_type #UFGT
accuracy #UFAC
gebco #UFGP
region #UFRG
for_scufn #SCUF
scufn #UFAD
height #SCHT
for_scar #SCAR
ant_pn_ref %CLCT/APNC
ant_pgaz_ref %CLCT/APGZ
-- ant_nz250000_map
-- ant_us250000_map
scar_id #SCID
scar_rec_by #SCRB
-- ant_info_notes
-- scar_desc
accuracy_rating #NTAR
desc_code #NTDC
rev_gaz_ref %NZGR
rev_treaty_legislation %TSLR

n.status as name_status_code,
gaz_plaintext(n.name) as ascii_name,
(select category from system_code where code_group='NSTS' and code=n.status) as name_status_category,
n.process as name_process_code,
f.status as feat_status_code,
f.feat_type as feat_type_code,
(select max(event_date) from name_event where authority='NZGB' and name_id=n.name_id) as last_nzgb_date,
(select event_type from name_event where authority='NZGB' and name_id=n.name_id order by event_date desc limit 1) as last_nzgb_event,
st_setsrid(f.ref_point,4326) as ref_point, 
        CASE
            WHEN (( SELECT count(*) AS count
               FROM gazetteer.feature_geometry
              WHERE feature_geometry.feat_id = n.feat_id)) = 0 THEN 'POINT'::text
            WHEN (( SELECT count(*) AS count
               FROM gazetteer.feature_geometry
              WHERE feature_geometry.feat_id = n.feat_id)) > 0 AND (( SELECT feature_geometry.geom_type
               FROM gazetteer.feature_geometry
              WHERE feature_geometry.feat_id = n.feat_id
             LIMIT 1)) = 'P'::bpchar THEN 'POLYGON'::text
            WHEN (( SELECT count(*) AS count
               FROM gazetteer.feature_geometry
              WHERE feature_geometry.feat_id = n.feat_id)) > 0 AND (( SELECT feature_geometry.geom_type
               FROM gazetteer.feature_geometry
              WHERE feature_geometry.feat_id = n.feat_id
             LIMIT 1)) = 'L'::bpchar THEN 'LINE'::text
            WHEN (( SELECT count(*) AS count
               FROM gazetteer.feature_geometry
              WHERE feature_geometry.feat_id = n.feat_id)) > 0 AND (( SELECT feature_geometry.geom_type
               FROM gazetteer.feature_geometry
              WHERE feature_geometry.feat_id = n.feat_id
             LIMIT 1)) = 'X'::bpchar THEN 'POINT'::text
            ELSE NULL::text
        END AS geom_type
from 
   name n
   join feature f on f.feat_id = n.feat_id
   join system_code ftsc on ftsc.code_group='FTYP' and ftsc.code=f.feat_type
   join system_code sts on sts.code_group='NSTS' and sts.code=n.status,
   nztm
where
   f.status = 'CURR' and
   f.feat_type not in (SELECT code FROM system_code where code_group='XNPF') and
   (select category from system_code where code_group='NSTS' and code=n.status)  != 'NPUB' and
   not exists (SELECT * from name_annotation na where na.name_id = n.name_id and na.annotation_type='NPUB') and
   not exists (SELECT * from feature_annotation fa where fa.feat_id = f.feat_id and fa.annotation_type='NPUB')
   ;

ALTER TABLE name_export
  OWNER TO gazetteer_dba;
  GRANT ALL ON TABLE name_export TO gazetteer_dba;
  GRANT SELECT ON TABLE name_export TO gazetteer_user;
  GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE name_export TO gazetteer_admin;

'''

sql = re.sub(r'^\s*([\wā]+)\s+\#(\w+)\s*$',  
             lambda m: (
             '''  (select 
             array_to_string(array_agg(annotation),' ') 
             from name_annotation na 
             where na.name_id=n.name_id and na.annotation_type= '''+
             "'"+m.group(2)+"'"+
             ' group by na.name_id) as '+m.group(1)+","
             ),sql,0,re.M)

sql = re.sub(r'^\s*(\w+)\s+\@(\w+)\s*$',  
             lambda m: (
             '''   (select 
             array_to_string(array_agg(annotation),' ') 
             from feature_annotation fa 
             where fa.feat_id=f.feat_id and fa.annotation_type='''+
                 "'"+m.group(2)+"'"+
             ' group by fa.feat_id) as '+m.group(1)+","
             ),sql,0,re.M)


sql = re.sub(r'^\s*(\w+)\s+\%(\w+)(?:\/(\w+))?\s*$',  
    lambda m:(
     '''   (select ref from (select
            event_reference as ref,
            event_date
            from name_event ne
            where ne.name_id = n.name_id 
            and  ne.event_type=''' + "'"+m.group(2)+ "'"+('''
            and  ne.authority='''+"'"+m.group(3)+"'" if m.group(3) else '') + '''
            order by event_date desc
            limit 1) as x)
            as '''+m.group(1)+","
            ), sql,0, re.M )

export_header_sql='''

DELETE FROM system_code where code_group in ('XCOL','XCRT','XCAT','XDSN','XDST','XDSC');
DELETE FROM system_code where code_group='CODE' and code in ('XCOL','XCRT','XCAT','XDSN','XDST','XDSC');
DELETE FROM system_code where code_group='CATE' and code in ('XCOL','XCRT','XDSN');

'''

syscode_sql = '''
INSERT INTO system_code(code_group,code,category,value,description)
VALUES ('{0}','{1}',{2},{3},{4});
'''

export_cols = '''
code_group|code|category|value|
CODE|XCOL|USER|Export data columns|
CODE|XCRT|USER|Export data filter criteria|
CODE|XCAT|USER|Export data category|
CODE|XDSN|USER|Export data set name|
CODE|XDSC|USER|Export data set categories|
CODE|XDST|USER|Export data set destination|
CATE|XCOL|XCAT|Export data category for column|
CATE|XCRT|XCAT|Export data category for filter criteri|
CATE|XDSN|XDST|Export data set destination|
XCAT|BASE||Common data|
XCAT|CPAN||CPA names|
XCAT|USEA||Undersea names|
XCAT|ANTA||Antarctic names|
XCAT|RCRD||Recorded names|
XCAT|REMV||Removed/replaced data|
XCAT|GMPT||Point geometry definition|
XCAT|REPT||Reporting support data|

XDST|LDSD||LDS data set|
XDST|CSVF||CSV file|
XDST|REPT||Reporting data|

XCOL|C010|BASE|name_id|
XCOL|C020|BASE|name|
XCOL|C030|BASE|status|
XCOL|C040|BASE|feat_type|
XCOL|C050|BASE|feat_id_src|
XCOL|C060|BASE|nzgb_ref|
XCOL|C070|BASE|district|
XCOL|C080|BASE|crd_projection|
XCOL|C090|BASE|crd_north|
XCOL|C100|BASE|crd_east|
XCOL|C110|BASE|crd_datum|
XCOL|C120|BASE|crd_latitude|
XCOL|C130|BASE|crd_longitude|
XCOL|C140|BASE|info_ref|
XCOL|C150|BASE|info_origin|
XCOL|C160|BASE|info_description|
XCOL|C170|BASE|info_note|
XCOL|C172|BASE|feat_note|
XCOL|C175|BASE|maori_name|
XCOL|C180|CPAN|cpa_legislation|
XCOL|C190|CPAN|cpa_section|
XCOL|C200|CPAN|conservancy|
XCOL|C210|CPAN|doc_cons_unit_no|
XCOL|C220|CPAN|doc_gaz_ref|
XCOL|C230|CPAN|treaty_legislation|
XCOL|C240|REPT|for_scufn|
XCOL|C250|USEA|accuracy|
XCOL|C260|USEA|gebco|
XCOL|C270|USEA|region|
XCOL|C280|USEA|scufn|
XCOL|C290|REPT|for_scar|
XCOL|C295|ANTA|height|
XCOL|C300|ANTA|ant_pn_ref|
XCOL|C310|ANTA|ant_pgaz_ref|
XCOL|C320|ANTA|ant_nz250000_map|
XCOL|C330|ANTA|ant_us250000_map|
XCOL|C340|ANTA|scar_id|
XCOL|C350|ANTA|scar_rec_by|
XCOL|C360|ANTA|ant_info_notes|
XCOL|C370|ANTA|scar_desc|
XCOL|C380|RCRD|accuracy_rating|
XCOL|C390|RCRD|desc_code|
XCOL|C400|REMV|rev_gaz_ref|
XCOL|C410|REMV|rev_treaty_legislation|
XCOL|C800|REPT|last_nzgb_date|
XCOL|C810|REPT|last_nzgb_event|
XCOL|C900|GMPT|ref_point|

XCRT|C010|OFFC|name_status_category = 'OFFC'|Select official names only

XDSN|CALL|CSVF|gaz_names_csv|All data CSV download
XDSC|CALL||BASE CPAN USEA ANTA RCRD REMV|All data CSV columns

XDSN|LDSA|LDSD|gaz_all_names|Gazetteer all names
XDSC|LDSA||BASE CPAN USEA ANTA RCRD REMV GMPT|A

XDSN|LDSO|LDSD|gaz_official_names|Gazetteer official names
XDSC|LDSO||BASE CPAN USEA ANTA RCRD REMV GMPT OFFC|Gazetteer official names only

XDSN|REPT|REPT|gaz_report_base_table|Published data table used as basis of reporting
XDSC|REPT||BASE CPAN USEA ANTA RCRD REMV GMPT REPT|Gazetteer official names only

'''.split("\n")

export_view_sql = '''
CREATE OR REPLACE VIEW
gazetteer_export_tables AS
WITH ds(code,category,name,cat_array) AS
(
SELECT 
   sc.code,
   sc.category,
   sc.value,
   CASE WHEN COALESCE(scc.value,'') = '' 
     THEN (SELECT array_agg(DISTINCT category) FROM system_code WHERE code_group='XCOL')
     ELSE regexp_split_to_array(trim(scc.value),E'\\\\s+')
     END
FROM
   system_code sc
   LEFT OUTER JOIN system_code scc ON scc.code_group='XDSC' AND scc.code=sc.code
WHERE
   sc.code_group='XDSN'
),
gnc(colname) as
(
select 
   lower(attname)
from 
   pg_attribute
where 
   attrelid='gazetteer.name_export'::regclass
)
SELECT 
   ds.code as data_set,
   ds.name as data_set_name,
   ds.category as data_set_type,
   (SELECT array_agg(RPAD(csc.code,4) || ':' || csc.value) 
       FROM
       system_code csc 
       WHERE csc.code_group='XCOL' AND
       csc.category in (SELECT c FROM unnest(ds.cat_array) as c)
       and lower(csc.value) in (select colname from gnc)
       )  AS data_columns,
   (SELECT array_agg(csc.value) 
       FROM
       system_code csc 
       WHERE csc.code_group='XCRT' AND
       csc.category in (SELECT c FROM unnest(ds.cat_array) as c)
       )  AS criteria
FROM 
   ds;

ALTER TABLE gazetteer_export_tables
  OWNER TO gazetteer_dba;
  GRANT ALL ON TABLE gazetteer_export_tables TO gazetteer_dba;
  GRANT SELECT ON TABLE gazetteer_export_tables TO gazetteer_user;
  GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE gazetteer_export_tables TO gazetteer_admin;

       
   '''

with open("gazetteer_export.sql","w") as f:
    f.write(sql)
    f.write(export_header_sql)
    for col in export_cols[1:]:
        parts = col.split('|')
        if len(parts) < 3 or parts[0] == 'code_group':
            continue
        if len(parts) < 4:
            parts[3]=parts[2]
        if not parts[3]:
            parts[3] = parts[2]
        parts[2] = "'"+parts[2].replace("'","''")+"'" if parts[2] else 'NULL'
        parts[3] = "'"+parts[3].replace("'","''")+"'" if parts[3] else 'NULL'
        parts[4] = "'"+parts[4].replace("'","''")+"'" if parts[4] else 'NULL'
        sql = re.sub(r'\{(\d)\}',lambda m: parts[int(m.group(1))],syscode_sql)
        f.write(sql)
    f.write(export_view_sql)
