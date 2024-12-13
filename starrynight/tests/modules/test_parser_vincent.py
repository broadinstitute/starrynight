"""Test vincent parser."""

from starrynight.parsers.common import ParserType, get_parser
from starrynight.parsers.transformer_vincent import VincentAstToIR


def test_parser_001():
    key = "cpg0999-merck-asma/merck/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_Channel405 nm,477 nm,G,T,A,C_Seq2069.tiff"
    path_parser = get_parser(ParserType.OPS_VINCENT)
    ast = path_parser.parse(key)
    transformer = VincentAstToIR()
    ir = transformer.transform(ast)
    pcp_index_dict = {
        k: v
        for item in ir["start"]
        for k, v in (item.items() if isinstance(item, dict) else {})
    }
    print(pcp_index_dict)


def test_parser_002():
    key = "cpg0999-merck-asma/merck/BATCH1/images/plate1/10X_c11_SBS-11/WellB2_PointB2_0347_ChannelnIR,GFP,DAPI_Seq1923.tiff"
    path_parser = get_parser(ParserType.OPS_VINCENT)
    ast = path_parser.parse(key)
    transformer = VincentAstToIR()
    ir = transformer.transform(ast)
    pcp_index_dict = {
        k: v
        for item in ir["start"]
        for k, v in (item.items() if isinstance(item, dict) else {})
    }
    print(pcp_index_dict)


def test_parser_003():
    key = "cpg0999-merck-asma/merck/BATCH1/images/plate2/10X_CP_plate2/WellB2_PointB2_0347_ChannelnIR,GFP,DAPI_Seq1923.tiff"
    path_parser = get_parser(ParserType.OPS_VINCENT)
    ast = path_parser.parse(key)
    transformer = VincentAstToIR()
    ir = transformer.transform(ast)
    pcp_index_dict = {
        k: v
        for item in ir["start"]
        for k, v in (item.items() if isinstance(item, dict) else {})
    }
    print(pcp_index_dict)
