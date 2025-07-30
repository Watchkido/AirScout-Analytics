### 1. Automatisierte Datenpipeline

```mermaid
graph TD
    A[CSV-Rohdaten] --> B(Data Cleaning)

    B --> C{Analyse-Modus}
    C -->|Standard| D[Grafische Auswertung]
    C -->|Expert| E[Machine Learning]
graph TD
    main_py[main.py\nmain()] --> pipeline[mod_000_pipeline.py\nmain()]
    pipeline --> laden_reinigen[mod_010_laden_reinigen.py\nladen_und_reinigen()\nmain()\nkurs_korrigieren()]
    laden_reinigen --> csv_analyzer[mod_020_csv_analyzer.py\nmain()\ncsv_info_extractor()\nerweiterte_sensor_analyse()\nmq_sensor_clustering()\nhauptkomponenten_analyse()]
    csv_analyzer --> feature_eng[mod_040_feature_engeneering.py\nfeature_engineering()\nstrassennamen_einfügen()\nmain()\nfinde_strasse_unscharf()\nextract_millisec()]
    feature_eng --> ppm_ugm3[mod_041_f_e_wert_ppm_µgm3.py\nconvert_to_ppm()\nconvert_to_ugm3()\nmain()]
    ppm_ugm3 --> glaetten[mod_042_glaetten_der_sensorwerte.py\nidentify_sensor_columns()\nmain()\ncalculate_zscore_analysis()\ndetect_gas_events()\ndetect_anomalies_ml()\nprint_analysis_summary()\nlog()]
    glaetten --> plotten[mod_050_datenanalyse_plotten.py\nplot_temperaturverlauf()\nplot_zeitslider_lautstaerke()\nplot_zeitslider_radioaktiv()\nplot_luftkarte()\nplot_sensorverläufe_mit_pdf()\nplot_sensoren_zeitverlauf()\nplot_3d()\nplot_beispiel_3()\nerstelle_plots()\nmain_plotting()\nmain()\nget_color()]
    plotten --> karte[mod_051_Karte_Luft_Qualitaet.py\nmain()]
    karte --> zeitslider[mod_052_zeitslider.py\nplot_zeitslider()\nerstelle_plots()\nmain_plotting()\nmain()]
    zeitslider --> korrel_top10[mod_053_korrel_und_TOP_10.py\nmain()\nluftqualitaet_index()]
    korrel_top10 --> textgen[mod_080_text_generieren.py\nlade_gemini_api_key()\ngeneriere_luftqualitaetsbericht_von_gemini()\ngeneriere_text()\nmain()]
    textgen --> gui[mod_100_gui.py\nshow_txt_in_tab()\nmain()\n__init__()\non_close()\nbeenden()\ncreate_tabs()]
    gui --> gps2street[gps2street.py\nreverse_geocode_gpsdatei()]



Funktionen in main.py:
  - main()

Funktionen in mod_000_pipeline.py:
  - main()

Funktionen in mod_010_laden_reinigen.py:
  - laden_und_reinigen()
  - main()
  - kurs_korrigieren()

Funktionen in mod_020_csv_analyzer.py:
  - main()
  - csv_info_extractor()
  - erweiterte_sensor_analyse()
  - mq_sensor_clustering()
  - hauptkomponenten_analyse()

Funktionen in mod_040_feature_engeneering.py:
  - feature_engineering()
  - strassennamen_einfügen()
  - main()
  - finde_strasse_unscharf()
  - extract_millisec()

Funktionen in mod_041_f_e_wert_ppm_µgm3.py:
  - convert_to_ppm()
  - convert_to_ugm3()
  - main()

Funktionen in mod_042_glaetten_der_sensorwerte.py:
  - identify_sensor_columns()
  - main()
  - calculate_zscore_analysis()
  - detect_gas_events()
  - detect_anomalies_ml()
  - print_analysis_summary()
  - log()

Funktionen in mod_050_datenanalyse_plotten.py:
  - plot_temperaturverlauf()
  - plot_zeitslider_lautstaerke()
  - plot_zeitslider_radioaktiv()
  - plot_luftkarte()
  - plot_sensorverläufe_mit_pdf()
  - plot_sensoren_zeitverlauf()
  - plot_3d()
  - plot_beispiel_3()
  - erstelle_plots()
  - main_plotting()
  - main()
  - get_color()

Funktionen in mod_051_Karte_Luft_Qualitaet.py:
  - main()

Funktionen in mod_052_zeitslider.py:
  - plot_zeitslider()
  - erstelle_plots()
  - main_plotting()
  - main()

Funktionen in mod_053_korrel_und_TOP_10.py:
  - main()
  - luftqualitaet_index()

Funktionen in mod_080_text_generieren.py:
  - lade_gemini_api_key()
  - generiere_luftqualitaetsbericht_von_gemini()
  - generiere_text()
  - main()

Funktionen in mod_100_gui.py:
  - show_txt_in_tab()
  - main()
  - __init__()
  - on_close()
  - beenden()
  - create_tabs()

Funktionen in gps2street.py:
  - reverse_geocode_gpsdatei()
