import math
import os
import enum
import ezdxf
from ._entity import Entity, EntityType
from .sketch import Sketch
from ._entity import Arc, Circle, Line, Point

def _get_linestyle(entity: Entity):
    return {"linetype": "DOTTED","color": ezdxf.colors.RED} if entity.isConstruction else {"linetype": "DOTTED","color": ezdxf.colors.BLUE}

def _dxf_draw_point(point: Point, msp: ezdxf.layouts.layout.Modelspace):
    msp.add_point((point.x,point.y),_get_linestyle(point))
    
def _dxf_draw_line(line: Line, msp: ezdxf.layouts.layout.Modelspace):
    msp.add_line(line.start_point,line.end_point,_get_linestyle(line))

def _dxf_draw_circle(circle: Circle, msp: ezdxf.layouts.layout.Modelspace):
    msp.add_circle((circle.xCenter,circle.yCenter), circle.radius, _get_linestyle(circle))

def _dxf_draw_arc(arc: Arc, msp: ezdxf.layouts.layout.Modelspace):
    startParam = arc.endParam * 180 / math.pi
    endParam = arc.startParam * 180 / math.pi
    if arc.clockwise:
        startParam, endParam = -endParam, -startParam
    msp.add_arc((arc.xCenter, arc.yCenter), arc.radius, startParam, endParam, arc.clockwise, dxfattribs=_get_linestyle(arc))

_DRAW_BY_TYPE = {
    Arc: _dxf_draw_arc,
    Circle: _dxf_draw_circle,
    Line: _dxf_draw_line,
    Point: _dxf_draw_point
}

def _dxf_draw(entity_item: tuple, msp: ezdxf.layouts.layout.Modelspace):
    entity_id, entity = entity_item
    # print("entity_id", entity_id)
    if type(entity) in [Arc,Circle,Line,Point]:
        draw_fn = _DRAW_BY_TYPE.get(type(entity))
        draw_fn(entity,msp)
    else:
        raise ValueError ("Unknown entity")

def sketch_to_dxf(sketch: Sketch, ignore_invalid_constraints: bool=True) -> ezdxf.document.Drawing:
    """Create a dxf format representation in terms of `NodeOp` and `EdgeOp` from the given sketch.

    All the entities in the sketch are converted, along with the respective constraints.
    Constraints are expressed in terms of entity indices (instead of original string identifiers).
    The sequence is ordered such that the nodes are in original insertion order, and the edges
    are placed such that they directly follow the last node they reference.

    Parameters
    ----------
    sketch : Sketch
        The sketch object to convert to sequence.
    ignore_invalid_constraints : bool
        If True, indicates that invalid constraints should be ignored. Otherwise, raises a ValueError
        on encountering an invalid constraint.

    Returns
    -------
    dxf_doc
        ezdxf.document.Drawing

    Raises
    ------
    ValueError
        If ``ignore_invalid_constraints`` is set to False, a ValueError will be raised
        upon encountering invalid constraints (e.g. constraints which refer to non-existing nodes,
        or whose parameters cannot be processed according to the specified schema).
    """
    dxf_doc = ezdxf.new("R12",setup=True)
    msp = dxf_doc.modelspace()
    for entity in sketch.entities.items():
        _dxf_draw(entity,msp)
    return dxf_doc

if __name__ == "__main__":
    ...
    # # cd to top-level directory
    # os.chdir('C:/UnSystems/desktop/DatasetTest/SketchGraphs')

    # import sketchgraphs.data as datalib
    # from sketchgraphs.data import flat_array
    # import sketchgraphs.onshape.call as onshape_call
    # seq_data = flat_array.load_dictionary_flat('../sequence_data/sg_t16_test.npy')
    # seq_data['sequences']

    # seq = seq_data['sequences'][100]
    # # print(*seq[:20], sep='\n')
    # sketch = datalib.sketch_from_sequence(seq)
    # datalib.render_sketch(sketch)
    # # datalib.render_sketch(sketch, hand_drawn=True)
    
    # a = sketch_to_dxf(sketch)
    # a.saveas('test.dxf')