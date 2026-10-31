import duckdb
import numpy as np
import pandas as pd

def run_comparison(iterations=10000):
    conn = duckdb.connect('data/goat.duckdb')
    
    # --- MODELO A: PURE ON-COURT ---
    df_z = conn.sql("SELECT * FROM gold.fct_goat_season_zscores").df()
    
    vol = df_z.groupby(['player_id', 'player_name']).agg(
        total_ws=('win_shares', 'sum'),
        total_vorp=('vorp', 'sum')
    ).reset_index()

    top5_z = (
        df_z.groupby('player_id')[['z_per', 'z_ws48', 'z_bpm', 'z_vorp']]
        .apply(lambda x: x.nlargest(5, 'z_vorp').mean())
        .reset_index()
        .rename(columns={
            'z_per': 'peak5_z_per', 'z_ws48': 'peak5_z_ws48',
            'z_bpm': 'peak5_z_bpm', 'z_vorp': 'peak5_z_vorp'
        })
    )

    stats_a = pd.merge(vol, top5_z, on='player_id')
    stats_a['z_total_ws'] = (stats_a['total_ws'] - stats_a['total_ws'].mean()) / stats_a['total_ws'].std()
    stats_a['z_total_vorp'] = (stats_a['total_vorp'] - stats_a['total_vorp'].mean()) / stats_a['total_vorp'].std()

    players = stats_a['player_name'].values
    n_players = len(players)

    # Simulação Modelo A
    ranks_a = np.zeros((iterations, n_players))
    alpha_a = [4.0, 4.0, 3.0, 3.0, 3.0, 4.0]
    mat_a = np.column_stack([
        stats_a['z_total_ws'].fillna(0), stats_a['z_total_vorp'].fillna(0),
        stats_a['peak5_z_per'].fillna(0), stats_a['peak5_z_ws48'].fillna(0),
        stats_a['peak5_z_bpm'].fillna(0), stats_a['peak5_z_vorp'].fillna(0)
    ])

    for i in range(iterations):
        scores_a = mat_a @ np.random.dirichlet(alpha_a)
        ranks_a[i] = n_players - np.argsort(np.argsort(scores_a))

    # --- MODELO B: PURE HARDWARE & ACCOLADES ---
    df_hw = conn.sql("SELECT * FROM gold.gold_player_hardware").df()
    # Garante alinhamento de ordem dos jogadores
    df_hw = pd.merge(pd.DataFrame({'player_name': players}), df_hw, on='player_name', how='left').fillna(0)

    # Normalização Z-score dos prêmios
    for col in ['mvp', 'fmvp', 'rings', 'all_nba', 'all_def']:
        df_hw[f'z_{col}'] = (df_hw[col] - df_hw[col].mean()) / (df_hw[col].std() + 1e-6)

    ranks_b = np.zeros((iterations, n_players))
    # Priors: Pesos para MVP, FMVP, Anéis, All-NBA, All-Defensive
    alpha_b = [5.0, 5.0, 4.0, 3.0, 2.0]
    mat_b = np.column_stack([
        df_hw['z_mvp'], df_hw['z_fmvp'], df_hw['z_rings'], df_hw['z_all_nba'], df_hw['z_all_def']
    ])

    for i in range(iterations):
        scores_b = mat_b @ np.random.dirichlet(alpha_b)
        ranks_b[i] = n_players - np.argsort(np.argsort(scores_b))

    # --- CONFRONTO FINAL ---
    df_compare = pd.DataFrame({
        'Jogador': players,
        'Rank_Modelo_A (Stats)': ranks_a.mean(axis=0),
        'Rank_Modelo_B (Hardware)': ranks_b.mean(axis=0)
    })
    
    df_compare['Diferença (B - A)'] = df_compare['Rank_Modelo_A (Stats)'] - df_compare['Rank_Modelo_B (Hardware)']
    df_compare = df_compare.sort_values('Rank_Modelo_B (Hardware)').reset_index(drop=True)

    print("\n==========================================================================")
    print("      CONFRONTO DE SENSIBILIDADE: MODELO A (STATS) VS MODELO B (HARDWARE)")
    print("==========================================================================")
    print(df_compare.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

if __name__ == "__main__":
    run_comparison()
