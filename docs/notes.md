# Notes

- First we create a test fixture, just 1 plate and a few images (specify this)


## Commands

```
starrynight inventory gen -d ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening -o ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace
```

```
starrynight index gen -i ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/inventory/inventory.parquet -o ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/index/
```

```
starrynight illum calc loaddata -i ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/index/index.parquet -o ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/cellprofiler/loaddata/cp/illum/illum_calc
```

```
starrynight illum calc cppipe -l ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/cellprofiler/loaddata/cp/illum/illum_calc/ -o ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/cellprofiler/cppipe/cp/illum/illum_calc -w ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace
```

```
starrynight cp -p ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/cellprofiler/cppipe/cp/illum/illum_calc/ -l ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/cellprofiler/loaddata/cp/illum/illum_calc -o ./scratch/dataset/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/illum/cp/illum_calc
```