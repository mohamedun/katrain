from katrain.core.game import KaTrainSGF


def branching_tree():
    root = KaTrainSGF.parse_sgf(
        "(;SZ[19](;B[aa])(;B[bb](;W[cc])(;W[dd](;B[ee];W[gg])(;B[ff]C[target];W[hh])(;B[ii]))))"
    )
    outer = root.children[1]
    parent = outer.children[1]
    target = parent.children[1]
    return root, outer, parent, target


def test_make_main_child_preserves_ancestors_siblings_and_descendants():
    root, outer, parent, target = branching_tree()
    root_order = root.children[:]
    outer_order = outer.children[:]
    old_first, _, old_third = parent.children
    descendants = target.children[:]

    target.promote_to_main_child()

    assert parent.children == [target, old_first, old_third]
    assert root.children == root_order
    assert outer.children == outer_order
    assert target.parent is parent
    assert target.children == descendants
    assert target.children[0].get_property("W") == "hh"


def test_local_promotion_survives_sgf_round_trip():
    root, _, _, target = branching_tree()
    target.promote_to_main_child()
    saved = KaTrainSGF.parse_sgf(root.sgf())

    assert [node.get_property("B") for node in saved.children] == ["aa", "bb"]
    outer = saved.children[1]
    assert [node.get_property("W") for node in outer.children] == ["cc", "dd"]
    assert [node.get_property("B") for node in outer.children[1].children] == ["ff", "ee", "ii"]
    assert outer.children[1].children[0].note == "target"


def test_root_and_already_main_child_are_unchanged():
    root, _, parent, _ = branching_tree()
    root_order = root.children[:]
    child_order = parent.children[:]

    root.promote_to_main_child()
    parent.children[0].promote_to_main_child()

    assert root.children == root_order
    assert parent.children == child_order
