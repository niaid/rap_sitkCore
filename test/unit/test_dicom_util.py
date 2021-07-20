from rap_sitkcore._dicom_util import convert_mv_ds_to_float_list, convert_float_list_to_mv_ds, keyword_to_gdcm_tag
import pytest


def test_convert1():
    d1 = [0.160145, 0.160114]
    rep1 = "0.160145\\0.160114 "  # space required per DICOM spec to have even bytes.

    assert d1 == convert_mv_ds_to_float_list(rep1)

    assert d1 == convert_mv_ds_to_float_list(rep1, vm=2)

    with pytest.raises(ValueError):
        convert_mv_ds_to_float_list(rep1, vm=1)

    with pytest.raises(ValueError):
        convert_mv_ds_to_float_list(rep1, vm=3)

    assert rep1 == convert_float_list_to_mv_ds(d1)


def test_keyword_to_gdcm_tag():

    assert keyword_to_gdcm_tag("PatientName") == "0010|0010"
    assert keyword_to_gdcm_tag("SeriesDescription") == "0008|103e"
    assert keyword_to_gdcm_tag("Modality") == "0008|0060"
    with pytest.raises(ValueError):
        keyword_to_gdcm_tag("modality")
