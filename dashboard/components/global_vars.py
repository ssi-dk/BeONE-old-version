import math

def assemblatron_diff(res):
    if "properties.denovo_assembly.summary.bin_length_at_1x" in res and "properties.denovo_assembly.summary.bin_length_at_10x" in res:
        res["properties.denovo_assembly.summary.bin_length_1x_10x_diff"] = res["properties.denovo_assembly.summary.bin_length_at_1x"] - \
            res["properties.denovo_assembly.summary.bin_length_at_10x"]
    else:
        res["properties.denovo_assembly.summary.bin_length_1x_10x_diff"] = math.nan
    return res

def assemblatron_contig_diff(res):
    if "properties.denovo_assembly.summary.bin_contigs_at_1x" in res and "properties.denovo_assembly.summary.bin_contigs_at_10x" in res:
        res["properties.denovo_assembly.summary.bin_contigs_1x_10x_diff"] = res["properties.denovo_assembly.summary.bin_contigs_at_1x"] - \
            res["properties.denovo_assembly.summary.bin_contigs_at_10x"]
    else:
        res["properties.denovo_assembly.summary.bin_contigs_1x_10x_diff"] = math.nan
    return res

FUNCS = [assemblatron_diff, assemblatron_contig_diff]

QC_COLUMNS = [
    # {
    #     "name": "Batch",
    #     "id": "sample_sheet.BatchNo"
    # },
    {
        "name": "Date",
        "id": "sample_sheet.BatchRunDate"
    },
    # {
    #     "name": "Sample Nr.",
    #     "id": "sample_sheet.SampleSupplied",
    #     'deletable': True,
    #     'renamable': True
    # },
    {
        "name": "Sample Name",
        "id": "sample_sheet.sample_name",
        'deletable': True,
        'renamable': True
    },
    {
        "name": "Type",
        "id": "sample_sheet.SampleType",
        'deletable': True,
        'renamable': True
    },
    {
        "name": "Sequence Date",
        "id": "sample_sheet.SequenceRunDate",
        'deletable': True,
        'renamable': True
    },
    {
        "name": "Run",
        "id": "sample_sheet.run_name",
        'deletable': True,
        'renamable': True
    },
    {
        "name": "Provided Specie",
        "id": "sample_sheet.provided_species",
        'deletable': True,
        'renamable': True
    }

]

COLUMNS = [
    {
        "name": "Run",
        "id": "sample_sheet.run_name"
    },
    {
        "name": "Name",
        "id": "sample_sheet.sample_name"
    },

    {
        "name": "Provided_Species",
        "id": "sample_sheet.provided_species"
    },
    # {
    #     "name": "Detected Species",
    #     "id": "properties.detected_species"
    # },

    {
        "name": "Run Date",
        "id": "sample_sheet.SequenceRunDate"
    }
]

plot_values = [
    {
        "name": "Genome_size_1x",
        "id": "properties.denovo_assembly.summary.bin_length_at_1x",
        "limits": [1500000, 6000000]
    },
    {
        "name": "Genome_size_10x",
        "id": "properties.denovo_assembly.summary.bin_length_at_10x",
        "limits": [1500000, 6000000],
        "xaxis": "x"
    },
    {
        "name": "G_size_difference_1x_10",
        "id": "properties.stamper.summary.test__denovo_assembly__genome_size_difference_1x_10x.value",
        "limits": [0, 260000]
    },
    {
        "name": "Avg_coverage",
        "id": "properties.denovo_assembly.summary.bin_coverage_at_1x",
        "limits": [0, 200]
    },
    {
        "name": "Contig_num_1x",
        "id": "properties.denovo_assembly.summary.bin_contigs_at_1x",
        "limits": [0, 700]
    },
    {
        "name": "Num_reads",
        "id": "properties.denovo_assembly.summary.filtered_reads_num",
        "limits": [1000, 8000000]
    },
    {
        "name": "Main_sp_plus_unclassified",
        "id": "properties.stamper.summary.test__species_detection__main_species_level.value",
        "limits": [0.75, 1]
    },
    {
        "name": "Unclassified_reads",
        "id": "properties.species_detection.summary.percent_unclassified",
        "limits": [0, 0.25]
    }
]

value_from_test = ["properties.stamper.summary.test__denovo_assembly__genome_size_difference_1x_10x",
                   "properties.stamper.summary.test__species_detection__main_species_level"]

ROUND_COLUMNS = ["properties.species_detection.summary.percent_unclassified",
                 "properties.denovo_assembly.summary.bin_coverage_at_1x"]

expected_results = ["resistance", "mlst", "plasmid",
                    "virulence"]  # expected categories in sample report

feedback_component = {
    "name": "user_feedback",
    "version": "1.0",
    "details": {
        "category": "stamper",
        "schema_version": 2,
        "target": "sample",
        "type": "stamper",
        "recommendation": "optional",
        "description": "This is generated by the web reporter when a user submits feedback.",
    },
    "dockerfile": None,
    "options": {},
    "resources": {},
    "requirements": {},
    "db_values_changes": {
        "sample": {
            "properties": {
                "stamper": {
                    "summary": None,
                    "component": {
                            "_id": None,
                            "date": None
                    }
                }
            }
        },
        "sample_component": {
            "summary": {
                "stamp": {
                    "name": None,
                    "value": None,
                    "display_name": None,
                    "date": None,
                    "status": None,
                    "reason": None
                }
            }
        }
    }
}
