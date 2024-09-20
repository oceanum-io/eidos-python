ROOTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
SCHEMAURL=https://schemas.oceanum.io/eidos
echo $SCHEMAURL

TMP=/tmp/eidoslib
mkdir -p $TMP

cd $TMP
rm -rf $TMP/*
mkdir $TMP/core
mkdir $TMP/viewnodes
mkdir $TMP/worldlayers

curl -s $SCHEMAURL/../features.json -o $TMP/features.json
curl -s $SCHEMAURL/root.json -o $TMP/core/root.json
curl -s $SCHEMAURL/dataspec.json -o $TMP/core/dataspec.json
curl -s $SCHEMAURL/node.json -o $TMP/core/node.json
curl -s $SCHEMAURL/state.json -o $TMP/core/state.json
curl -s $SCHEMAURL/viewnodes/plot.json -o $TMP/viewnodes/plot.json
curl -s $SCHEMAURL/viewnodes/world.json -o $TMP/viewnodes/world.json
curl -s $SCHEMAURL/viewnodes/document.json -o $TMP/viewnodes/document.json
for layer in feature grid label scenegraph sea_surface track ; do
    curl -s $SCHEMAURL/worldlayers/$layer.json -o $TMP/worldlayers/$layer.json
done

Create a stub for the vega-lite schema
echo "{
    \"description\": \"Vega or Vega-Lite specification\",
    \"type\": \"object\",
    \"definitions\": {
        \"TopLevelSpec\": {
            \"title\":\"Vega spec\",
            \"description\": \"Top-level specification of a Vega or Vega-Lite visualization\",
            \"type\": \"object\",
            \"properties\": {
            }
        },
    },
    
}" > $TMP/vegaspec.json

# Replace schema references
perl -p -i -e "s|https\:\/\/schemas\.oceanum\.io\/eidos\/viewnodes|$TMP\/viewnodes|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/schemas\.oceanum\.io\/eidos\/worldlayers|$TMP\/worldlayers|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/schemas\.oceanum\.io\/eidos|$TMP\/core|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/schemas\.oceanum\.io\/features|$TMP\/features|g" $TMP/*/*.json
perl -p -i -e "s|https\:\/\/vega\.github\.io\/schema\/vega-lite\/v5.json|$TMP/vegaspec.json|g" $TMP/viewnodes/plot.json

datamodel-codegen --input-file-type jsonschema --input $TMP --output $ROOTDIR/oceanum/eidos/ --output-model-type pydantic_v2.BaseModel --base-class=oceanum.eidos._basemodel.EidosModel --use-subclass-enum --use-schema-description --use-field-description

#Patch codegen bug
perl -p -i -e "s|viewnodesworld|viewnodes\.world|g" $ROOTDIR/oceanum/eidos/worldlayers/*.py
perl -p -i -e "s|layerSpec: LayerSpec|layerSpec: Any|g" $ROOTDIR/oceanum/eidos/viewnodes/world.py

python $ROOTDIR/autogen/gen_init.py

#vegaspec is a special case - copy Altair wrapper to vegaspec.py
cp $ROOTDIR/autogen/_vegaspec.py $ROOTDIR/oceanum/eidos/vegaspec.py

