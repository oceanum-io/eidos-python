ROOTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
SCHEMAURL=https://schemas.oceanum.io/eidos
echo $SCHEMAURL

# Extract version from root schema
TMP=/tmp/eidoslib
mkdir -p $TMP

cd $TMP
rm -rf $TMP/*
mkdir $TMP/node
mkdir $TMP/node/world

curl -s $SCHEMAURL/../features.json -o $TMP/features.json
curl -s $SCHEMAURL/root.json -o $TMP/core/root.json
curl -s $SCHEMAURL/dataspec.json -o $TMP/core/dataspec.json
curl -s $SCHEMAURL/state.json -o $TMP/core/state.json
curl -s $SCHEMAURL/theme.json -o $TMP/core/theme.json
curl -s $SCHEMAURL/node/plot.json -o $TMP/node/plot.json
curl -s $SCHEMAURL/node/world.json -o $TMP/node/world.json
curl -s $SCHEMAURL/node/document.json -o $TMP/node/document.json

for layer in feature gridded label scenegraph sea_surface track ; do
    curl -s $SCHEMAURL/node/worldlayer/$layer.json -o $TMP/node/worldlayer/$layer.json
done

#cp -RL $ROOTDIR/../../packages/schemas/src/eidos/* $TMP

# Extract version from root schema in TMP directory
VERSION=$(grep -o '"const": "[^"]*"' "$TMP/root.json" | head -1 | cut -d'"' -f4)
echo "Extracted version from schema: $VERSION"

# Create version file
echo "# Auto-generated file - DO NOT EDIT
__version__ = \"$VERSION\"
" > "$ROOTDIR/oceanum/eidos/version.py"
echo "Created version.py with version $VERSION"

#Create a stub for the vega-lite schema
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

# Replace vega schema reference with a stub
perl -p -i -e "s|https\:\/\/vega\.github\.io\/schema\/vega-lite\/v5.json|$TMP/vegaspec.json|g" $TMP/node/plot.json

datamodel-codegen --input-file-type jsonschema --input $TMP --output $ROOTDIR/oceanum/eidos/ --output-model-type pydantic_v2.BaseModel --base-class=oceanum.eidos._basemodel.EidosModel --use-subclass-enum --use-schema-description --use-field-description

python $ROOTDIR/autogen/gen_init.py

#vegaspec is a special case - copy Altair wrapper to vegaspec.py
cp $ROOTDIR/autogen/_vegaspec.py $ROOTDIR/oceanum/eidos/vegaspec.py
