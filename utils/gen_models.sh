ROOTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
SCHEMADIR=${ROOTDIR}/../../packages/schemas/src
echo $SCHEMADIR

TMP=/tmp/eidoslib
mkdir -p $TMP

cd $TMP
rm -rf $TMP/*

cp -rL $SCHEMADIR/* $TMP
rm $TMP/vega.json
mv $TMP/eidos $TMP/core

#Create a stub for the vega-lite schema
echo "{
    \"description\": \"Vega or Vega-Lite specification\",
    \"type\": \"object\",
    \"definitions\": {
        \"VegaSpec\": {
            \"title\":\"Vega spec\",
            \"description\": \"Top-level specification of a Vega or Vega-Lite visualization\",
            \"type\": \"object\",
            \"properties\": {
            }
        },
        \"TopLevelSpec\":{
            \"\$ref\": \"#/definitions/VegaSpec\"
        }
    },
    
}" > $TMP/vegaspec.json

# Replace schema references


perl -p -i -e "s|https\:\/\/oceanum\.io\/schemas\/eidos\/viewnodes|$TMP\/viewnodes|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/oceanum\.io\/schemas\/eidos\/worldlayers|$TMP\/worldlayers|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/oceanum\.io\/schemas\/eidos|$TMP\/core|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/oceanum\.io\/schemas|$TMP|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/vega\.github\.io\/schema\/vega-lite\/v5.json|$TMP/vegaspec.json|g" $TMP/viewnodes/plot.json

datamodel-codegen --input-file-type jsonschema --input $TMP --output $ROOTDIR/eidos/ --output-model-type pydantic_v2.BaseModel --base-class=eidos._basemodel.EidosModel --use-subclass-enum --use-schema-description --use-field-description
python $ROOTDIR/utils/gen_init.py

