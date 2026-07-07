ROOTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
SCHEMAURL=https://schemas.oceanum.io/eidos
echo $SCHEMAURL

# Extract version from root schema
TMP=/tmp/eidoslib
mkdir -p $TMP

cd $TMP
rm -rf $TMP/*
mkdir $TMP/node
mkdir $TMP/node/worldlayer

curl -s $SCHEMAURL/../geojson.json -o $TMP/geojson.json
curl -s $SCHEMAURL/root.json -o $TMP/core/root.json
curl -s $SCHEMAURL/data.json -o $TMP/core/data.json
curl -s $SCHEMAURL/common.json -o $TMP/core/common.json
curl -s $SCHEMAURL/panel.json -o $TMP/core/panel.json
curl -s $SCHEMAURL/theme.json -o $TMP/core/theme.json
curl -s $SCHEMAURL/node/plot.json -o $TMP/node/plot.json
curl -s $SCHEMAURL/node/world.json -o $TMP/node/world.json
curl -s $SCHEMAURL/node/document.json -o $TMP/node/document.json

for layer in feature gridded label scenegraph seasurface track pointcloud; do
    curl -s $SCHEMAURL/node/worldlayer/$layer.json -o $TMP/node/worldlayer/$layer.json
done

cp -RL $ROOTDIR/../../packages/schemas/src/eidos/* $TMP

# Extract version from npm package.json
VERSION=$(node -p "require('$ROOTDIR/../../package.json').version")
echo "Extracted version from npm package: $VERSION"

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
perl -p -i -e "s|https\:\/\/vega\.github\.io\/schema\/vega-lite\/v6.json|$TMP/vegaspec.json#/definitions/TopLevelSpec|g" $TMP/node/plot.json

# Resolve circular dependency by removing menu node from grid
perl -p -i -e "s|menu.json|document.json|g" $TMP/node/grid.json



datamodel-codegen --input-file-type jsonschema --input $TMP --output $ROOTDIR/oceanum/eidos/ --output-model-type pydantic_v2.BaseModel --base-class=oceanum.eidos._basemodel.EidosModel --use-subclass-enum --use-schema-description --use-field-description

python $ROOTDIR/autogen/gen_init.py

# Fix circular import: world.py imports panel, but panel.py imports world (via node/__init__.py).
# Remove the panel import from world.py and defer all model_rebuild() calls that transitively
# reference panel.EidosPanel (World, Grid, Menu) to panel.py, where panel is fully defined.
WORLD_PY=$ROOTDIR/oceanum/eidos/node/world.py
GRID_PY=$ROOTDIR/oceanum/eidos/node/grid.py
MENU_PY=$ROOTDIR/oceanum/eidos/node/menu.py
PANEL_PY=$ROOTDIR/oceanum/eidos/panel.py

# Remove `panel` from world.py's import and its model_rebuild() call
perl -p -i -e "s|from \.\. import common, panel|from .. import common|g" $WORLD_PY
perl -p -i -e "s|^World\.model_rebuild\(\)$|# model_rebuild() called in panel.py after EidosPanel is defined to break circular import|g" $WORLD_PY

# Defer Grid.model_rebuild() - Grid references World which references panel.EidosPanel
perl -p -i -e "s|^Grid\.model_rebuild\(\)$|# model_rebuild() called in panel.py after EidosPanel is defined to break circular import|g" $GRID_PY

# Defer Menu.model_rebuild() - Menu references World which references panel.EidosPanel
perl -p -i -e "s|^Menu\.model_rebuild\(\)$|# model_rebuild() called in panel.py after EidosPanel is defined to break circular import|g" $MENU_PY

# In panel.py, rebuild deferred models with panel in the types namespace
perl -p -i -e "s|^EidosPanel\.model_rebuild\(\)$|import sys as _sys\n_panel_ns = {\"panel\": _sys.modules[__name__]}\nworld.World.model_rebuild(_types_namespace=_panel_ns)\ngrid.Grid.model_rebuild(_types_namespace=_panel_ns)\nmenu.Menu.model_rebuild(_types_namespace=_panel_ns)\nEidosPanel.model_rebuild()|g" $PANEL_PY

#vegaspec is a special case - copy Altair wrapper to vegaspec.py
cp $ROOTDIR/autogen/_vegaspec.py $ROOTDIR/oceanum/eidos/vegaspec.py
