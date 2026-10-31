import duckdb
import numpy as np
import pandas as pd

def run_simulation(iterations=10000):
    conn = duckdb.connect('data/goat.duckdb')
    
    # Carrega métricas z-score e volume
    df_z = conn.sql("""
        SELECT 
            player_id,
            player_name,
            season_end_year,
            win_shares,
            vorp,
            z_per,
            z_ws48,
            z_bpm,
            z_vorp
        FROM gold.fct_goat_season_zscores
    """).df()
    
    # 1. Volume Total (Acumulado)
    vol = df_z.groupby(['player_id', 'player_name']).agg(
        total_ws=('win_shares', 'sum'),
        total_vorp=('vorp', 'sum'),
        seasons=('season_end_year', 'count')
    ).reset_index()

    # 2. Pico de Eficiência (Média das 5 melhores temporadas por jogador)
    top5_z = (
        df_z.groupby('player_id')[['z_per', 'z_ws48', 'z_bpm', 'z_vorp']]
        .apply(lambda x: x.nlargest(5, 'z_vorp').mean())
        .reset_index()
        .rename(columns={
            'z_per': 'peak5_z_per',
            'z_ws48': 'peak5_z_ws48',
            'z_bpm': 'peak5_z_bpm',
            'z_vorp': 'peak5_z_vorp'
        })
    )

    stats = pd.merge(vol, top5_z, on='player_id')

    # Normalização Z-score dos agregados
    stats['z_total_ws'] = (stats['total_ws'] - stats['total_ws'].mean()) / stats['total_ws'].std()
    stats['z_total_vorp'] = (stats['total_vorp'] - stats['total_vorp'].mean()) / stats['total_vorp'].std()

    players = stats['player_name'].values
    n_players = len(players)
    ranks = np.zeros((iterations, n_players))

    # Priors Dirichlet: Balanceamento de Volume Acumulado e Pico de Eficiência
    alpha_priors = [4.0, 4.0, 3.0, 3.0, 3.0, 4.0]

    matrix_stats = np.column_stack([
        stats['z_total_ws'].fillna(0).values,
        stats['z_total_vorp'].fillna(0).values,
        stats['peak5_z_per'].fillna(0).values,
        stats['peak5_z_ws48'].fillna(0).values,
        stats['peak5_z_bpm'].fillna(0).values,
        stats['peak5_z_vorp'].fillna(0).values
    ])

    for i in range(iterations):
        weights = np.random.dirichlet(alpha_priors)
        scores = matrix_stats @ weights
        ranks[i] = n_players - np.argsort(np.argsort(scores))

    df_res = pd.DataFrame({
        'player_name': players,
        'mean_rank': ranks.mean(axis=0),
        'p1_probability': (ranks == 1).mean(axis=0) * 100,
        'top3_probability': (ranks <= 3).mean(axis=0) * 100,
        'top5_probability': (ranks <= 5).mean(axis=0) * 100
    }).sort_values('mean_rank').reset_index(drop=True)

    print("\n--- MODELO A: PURE ON-COURT (VOLUME + PICO 5 ANOS) ---")
    print(df_res.head(15).to_string(index=False))

if __name__ == "__main__":
    run_simulation()
