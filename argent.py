import streamlit as st
import pandas as pd
import base64
import requests
import altair as alt
from io import BytesIO
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Charger le fichier CSV et preparation -------------------------
@st.cache_data
def load_data():
    url = "https://www.data.gouv.fr/fr/datasets/r/3f360fdd-39e5-4dda-9553-3d2a00ceabae"
    response = requests.get(url)
    data = pd.read_csv(BytesIO(response.content), sep=';')
    data = prepare_data(data)
    return data

@st.cache_data
def prepare_data(data):
    # Supprimer les lignes où le montant est négatif ou égal à zéro
    data = data[data['montant'] > 0]

    # Supprimer les colonnes spécifiées
    columns_to_drop = [
        'agregat_niveau', 'ordre_analyse1_section1', 'ordre_analyse1_section2',
        'ordre_analyse1_section3', 'ordre_analyse2_section1', 'ordre_analyse2_section2',
        'ordre_analyse2_section3', 'ordre_analyse3_section1', 'ordre_analyse3_section2',
        'ordre_analyse3_section3', 'ordre_analyse4_section1', 'ordre_affichage',
        'ident', 'nomen', 'siren','cbudg'
    ]
    data = data.drop(columns=columns_to_drop)

    return data

def categorize_agregat(agregat): #créé la colonne catégorie qui contient Dépense Recette ou autre
    # Classe les agrégats en dépenses
    depenses_agregats = [
        'Dépenses',
        'Dépenses totales',
        'Dépenses totales hors remboursement du capital de la dette',
        'Dépenses - Fonctionnement',
        'Dépenses de fonctionnement',
        'Achats et charges externes',
        'Frais de personnel',
        'Charges financières',
        'Dépenses d\'intervention',
        'Subventions aux personnes de droit privé',
        'Contributions aux organismes de transport',
        'Dépenses - Investissement',
        'Dépenses d\'investissement',
        'Remboursements d\'emprunts hors gestion active de la dette',
        'Dépenses d\'investissement hors remboursement du capital de la dette',
        'Dépenses d\'équipement',
        'Subventions d\'équipement versées',
        'Subventions d\'équipement versées aux communes et aux groupements',
        'Annuité de la dette',
    ]

    # Classe les agrégats en recettes
    recettes_agregats = [
        'Recettes',
        'Recettes totales',
        'Recettes totales hors emprunts',
        'Recettes - Fonctionnement',
        'Recettes de fonctionnement',
        'Impôts et taxes',
        'Impôts locaux',
        'Autres impôts et taxes',
        'Cartes grises',
        'CVAE',
        'TICPE',
        'TVA',
        'Concours de l\'Etat',
        'Dotation globale de fonctionnement',
        'Péréquations et compensations fiscales',
        'Autres dotations de fonctionnement',
        'Subventions reçues et participations',
        'Ventes de biens et services',
        'Recettes - Investissement',
        'Recettes d\'investissement',
        'Emprunts hors gestion active de la dette',
        'Recettes d\'investissement hors emprunts',
        'FCTVA',
        'Autres dotations et subventions',
        'DRES',
        'Produit des cessions d\'immobilisations',
    ]

    if agregat in depenses_agregats:
        return 'Dépenses'
    elif agregat in recettes_agregats:
        return 'Recettes'
    else:
        return 'Autres'


@st.cache_data
def barre_gauche():

    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = True


    # Afficher la barre latérale si l'option est activée
    if st.session_state.show_sidebar:
        # Les informations que vous souhaitez afficher dans la barre latérale
        st.sidebar.write("Vincent Reslou")
        st.sidebar.write("Promo 2014")
        st.sidebar.write("M1 BIA2")
        st.sidebar.write("[Linkedin/vincent.reslou](https://www.linkedin.com/in/vincent-reslou/)")
        st.sidebar.write(" #datavz2023efrei")

@st.cache_data
def get_table_download_link(dataframe): # Fonction pour créer un lien de téléchargement du CSV
    csv = dataframe.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="comptes_regions.csv">Télécharger le CSV</a>'
    return href

#-------------------------------------------


def pres_donnee(data): #premier apercu des données
    # Aperçu des données
    st.header("Aperçu des données")
    st.write("Les données présentent des informations financières des régions de 2012 à 2022.")

    # Sélection des colonnes à afficher
    default_columns = ["exer","reg_name","montant","agregat"]
    selected_columns = st.multiselect("Sélectionnez les colonnes à afficher :", data.columns,default=default_columns)

    # Filtrage des données par colonnes sélectionnées
    if selected_columns:
        st.subheader("Données sélectionnées")

        st.write(data[selected_columns])

    # Statistiques descriptives      Finalement peut-être pas très interessant
    #st.subheader("Statistiques descriptives")
    #st.write("Voici quelques statistiques clés des données sélectionnées :")
    #if selected_columns:
    #    st.write(data[selected_columns].describe())

def analyse(data): #premiere analyse

    # Analyse par région
    st.subheader("Analyse par région")
    st.write("Nous pouvons examiner le nombre d'entrée par région.")
    region_counts = data["reg_name"].value_counts()
    st.bar_chart(region_counts)

    st.write("On observe qu'il y a bien plus d'entré pour les régions que pour les CTU.")
    category_counts = data["categ"].value_counts()
    st.bar_chart(category_counts)

    # Évolution des dépenses et des recettes
    st.title("Évolution du montant des dépenses et des recettes au fil des années pour l'ensemble des régions")

    data_grouped_depenses = data[data['categorie'] == 'Dépenses'].groupby('exer')['montant'].sum()
    data_grouped_recettes = data[data['categorie'] == 'Recettes'].groupby('exer')['montant'].sum()

    # graph
    fig, ax = plt.subplots(figsize=(12, 6))
    data_grouped_depenses.plot(kind='line', label='Dépenses', color='skyblue', ax=ax)
    data_grouped_recettes.plot(kind='line', label='Recettes', color='lightcoral', ax=ax)

    ax.set_title("Évolution des dépenses et des recettes au fil des années")
    ax.set_xlabel("Année")
    ax.set_ylabel("Montant")
    ax.legend()


    st.pyplot(fig)


    data_grouped = data.groupby('categorie')['montant'].sum() # graph en barres
    fig, ax = plt.subplots(figsize=(10, 6))
    data_grouped.plot(kind='bar', color=['skyblue', 'lightcoral'], ax=ax)
    ax.set_title("Comparaison de la somme des Dépenses et des Recettes")
    ax.set_xlabel("Catégorie")
    ax.set_ylabel("Somme des montants")
    ax.set_xticklabels(data_grouped.index, rotation=0)
    st.pyplot(fig)


def graph(data):
    # Évolution des dépenses
    depenses_data = data[data['categorie'] == 'Dépenses']
    years_options_depenses = sorted(depenses_data['exer'].unique())
    regions_options_depenses = sorted(depenses_data['reg_name'].unique())
    regions_options_depenses.insert(0, "Toutes les régions")

    st.title("Somme des montants des dépenses par année et région")
    selected_years_depenses = st.multiselect("Sélectionnez les années :", years_options_depenses, key="depenses_years")
    selected_regions_depenses = st.multiselect("Sélectionnez les régions :", regions_options_depenses, key="depenses_regions")

    if "Toutes les régions" in selected_regions_depenses:
        filtered_data_depenses = depenses_data[depenses_data['exer'].isin(selected_years_depenses)]
    else:
        filtered_data_depenses = depenses_data[(depenses_data['exer'].isin(selected_years_depenses)) & (depenses_data['reg_name'].isin(selected_regions_depenses))]

    if not filtered_data_depenses.empty:
        chart_depenses = alt.Chart(filtered_data_depenses).mark_line().encode(
            x='exer:O',
            y='sum(montant):Q',
            color='reg_name:N'
        ).properties(width=700, height=400, title="Somme des montants des dépenses par année et région")

        st.altair_chart(chart_depenses)


    # Évolution des recettes
    recettes_data = data[data['categorie'] == 'Recettes']
    years_options_recettes = sorted(recettes_data['exer'].unique())
    regions_options_recettes = sorted(recettes_data['reg_name'].unique())
    regions_options_recettes.insert(0, "Toutes les régions")

    st.title("Somme des montants des recettes par année et région")
    selected_years_recettes = st.multiselect("Sélectionnez les années :", years_options_recettes, key="recettes_years")
    selected_regions_recettes = st.multiselect("Sélectionnez les régions :", regions_options_recettes, key="recettes_regions")

    if "Toutes les régions" in selected_regions_recettes:
        filtered_data_recettes = recettes_data[recettes_data['exer'].isin(selected_years_recettes)]
    else:
        filtered_data_recettes = recettes_data[(recettes_data['exer'].isin(selected_years_recettes)) & (recettes_data['reg_name'].isin(selected_regions_recettes))]

    if not filtered_data_recettes.empty:
        chart_recettes = alt.Chart(filtered_data_recettes).mark_line().encode(
            x='exer:O',
            y='sum(montant):Q',
            color='reg_name:N'
        ).properties(width=700, height=400, title="Somme des montants des recettes par année et région")

        st.altair_chart(chart_recettes)

def depense_par_hab(data):

    st.title("Dépenses par habitant par région en moyenne sur la période 2012-2022")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Filtre
    depenses_data = data[data['categorie'] == 'Dépenses']

    # Groupe par région et calcule la moyenne des dépenses par habitant
    avg_eurs_per_habitant = depenses_data.groupby('reg_name')['euros_par_habitant'].mean().sort_values(ascending=False)

    # graph à barres horizontales
    avg_eurs_per_habitant.plot(kind='barh', ax=ax)
    ax.set_xlabel("Dépenses par habitant (en euros)")
    ax.set_ylabel("Région")
    ax.set_title("Dépenses par habitant par région")

    st.pyplot(fig)

def agregat(data): #on s'interesse plus sur les agregats

    # Regroupe par agrégat et calcule la somme des montants pour chaque agrégat
    agregat_sum = data.groupby('agregat')['montant'].sum().reset_index()

    st.write("Somme des montants par agrégat :")
    st.write(agregat_sum)

    # Regroupe par région et agrégat, puis calcule la somme des montants pour chaque combinaison
    region_agregat_sum = data.groupby(['reg_name', 'agregat'])['montant'].sum().reset_index()
    # Trie dans l'ordre décroissant
    region_agregat_sum = region_agregat_sum.sort_values(by='montant', ascending=False)
    st.write("Agrégats les plus chers :")
    st.write(region_agregat_sum)

    #pas le meilleur graph
    top_agregats = region_agregat_sum.groupby('reg_name').head(5)
    plt.figure(figsize=(10, 8))
    for region, data in top_agregats.groupby('reg_name'):
        plt.barh(data['agregat'], data['montant'], label=region)

    plt.xlabel('Montant')
    plt.ylabel('Agrégat')
    plt.title('Agrégats les plus chers par région')
    plt.legend()
    st.pyplot(plt)


    total_agregat = data.groupby('agregat')['montant'].sum()

    # Camembert montrant la somme du montant de chaque agrégat
    st.write("Somme du montant de chaque agrégat pour toutes les régions")
    fig, ax = plt.subplots()
    ax.pie(total_agregat, labels=total_agregat.index, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

def search(data):
    # Recherche dans les données
    st.subheader("Recherche dans les données")
    st.write("Vous pouvez rechercher des informations spécifiques dans les données.")
    search_term = st.text_input("Rechercher dans les données")
    search_results = data[data.apply(lambda row: any(search_term.lower() in str(cell).lower() for cell in row), axis=1)]
    if not search_results.empty:
        st.write("Résultats de la recherche :")
        st.write(search_results)
    else:
        st.warning("Aucun résultat trouvé pour la recherche.")





def depense_par_region_camembert(data):
    # Regroup  par région et calcule la somme des dépenses par région
    region_expenses = data.groupby('reg_name')['montant'].sum()

    # camembert
    fig, ax = plt.subplots()
    ax.pie(region_expenses, labels=region_expenses.index, autopct='%1.1f%%', startangle=90)

    ax.set_title('Dépenses par région')
    st.pyplot(fig)

def camembert_par_region(data, selected_region):

    # Filtre pour garder une seul region
    region_data = data[data['reg_name'] == selected_region]

    st.title(f'Dépenses par agrégat - {selected_region}')
    # Regroupe agrégat et calcule la somme des dépenses par agrégat
    agregat_expenses = region_data.groupby('agregat')['montant'].sum()

    # Sélectionne les 10 agrégats les plus importants
    top_agregats = agregat_expenses.nlargest(10)

    # Regroupe le reste dans "Autre"
    other_agregats = agregat_expenses[~agregat_expenses.index.isin(top_agregats.index)]
    top_agregats['Autre'] = other_agregats.sum()

    # camembert
    fig, ax = plt.subplots()
    ax.pie(top_agregats, labels=top_agregats.index, autopct='%1.1f%%', startangle=90)
    st.pyplot(fig)





# Fonction pour créer un graphique de densité
def graph_densite(data):
    st.title("Graphique de Densité des Dépenses par Catégorie")
    st.write("Utilisez un graphique de densité pour montrer comment les dépenses sont réparties par catégorie.")

    # cree le graph
    density_chart = alt.Chart(data).transform_density(
        density='montant',
        groupby=['reg_name']
    ).mark_area().encode(
        x=alt.X('value:Q', title="montant"),
        y=alt.Y('density:Q', title=""),
        color='reg_name:N'
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(density_chart, use_container_width=True)


def heatmap(data):
    # Sélectionner les colonnes numériques
    numerical_columns = data.select_dtypes(include=[np.number])
    # Calculer la matrice de corrélation
    correlation_matrix = numerical_columns.corr()

    st.title("Heatmap de corrélation entre les informations")
    st.write("Ce graphique représente la corrélation entre les différebtes information. cbudg étant s'il s'agit d'un budget principal ou annexe")

    plt.figure(figsize=(10, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)

    st.pyplot(plt)

def main():
    data = load_data()  #charge data et les modifies
    barre_gauche()  #affiche la barre a gauche
    data['categorie'] = data['agregat'].apply(categorize_agregat) #créé la colonne categorie

    st.title("Présentation des Comptes des régions 2012-2022")
    pres_donnee(data)

    analyse(data)
    depense_par_region_camembert(data)
    graph(data)
    depense_par_hab(data)

    selected_region = st.selectbox("Sélectionnez une région :", data['reg_name'].unique())
    camembert_par_region(data, selected_region)

    agregat(data)
    search(data)

    graph_densite(data)
    heatmap(data)


    download_link = get_table_download_link(data) #cree un lien pour telecharger le csv utilisé apres load_data
    st.markdown(download_link, unsafe_allow_html=True) #affiche le lien

    st.text("Analyse des Comptes des régions 2012-2021 réalisée avec Streamlit.")




if __name__ == '__main__':
    main()


