Store and Fetch GFS backgrounds
---

`gfs_store.py` and `gfs_fetch.py` are scripts to store and fetch GFS backgrounds into and from a R2D2 database.
The configuration is specified via `gfs-config.yaml`

### Usage
```
# To store into R2D2 database from a ROTDIR structure in `fc_root`:
python gfs_store.py
```

```
# To fetch from an R2D2 database into a ROTDIR structure in `stage`:
python gfs_fetch.py
```
