DROP TABLE IF EXISTS runs;

CREATE TABLE runs (
    run_id INTEGER,
    p_bar REAL NOT NULL,
    n_stages INTEGER NOT NULL,
    feed_stage INTEGER NOT NULL,
    reflux REAL NOT NULL,
    B_kmol_h REAL NOT NULL,
    converged INTEGER NOT NULL CHECK (converged IN (0, 1)),
    error_msg TEXT,
    x_thf_top REAL,
    x_thf_bottom REAL,
    q_cond_kw REAL,
    q_reb_kw REAL,
    T_top_C REAL,
    T_bottom_C REAL,
    D_kmol_h REAL,
    thf_err_rel REAL,
    PRIMARY KEY (run_id)
);