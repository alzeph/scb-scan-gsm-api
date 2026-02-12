from rest_framework import serializers
from django.db import transaction
from gsm_coverage.models import CSVLine, GSMScan, GSMData
import pandas as pd


class CSVLineSerializer(serializers.ModelSerializer):
    """
    Serializer pour les lignes individuelles du CSV.
    Permet de valider et de sérialiser chaque entrée avant insertion en base.
    """
    class Meta:
        model = CSVLine
        fields = [
            'pk',
            'time', 'lat', 'lon', 'alt', 'gps_fix',
            'rat', 'mccmnc', 'cell_id',
            'pci',
            'band', 'earfcn',
            'rsrp_dbm', 'rsrq_db', 'sinr_db'
        ]


class GSMScanSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour GSMScan.
    Vérifie que le fichier uploadé est un CSV valide et que toutes les colonnes attendues sont présentes.
    Crée ensuite des instances CSVLine pour chaque ligne du fichier.
    """
    
    csv_lines = CSVLineSerializer(many=True, read_only=True, required=False)
    operator = serializers.CharField(write_only=True)
    class Meta:
        model = GSMScan
        fields = [
            'pk',
            'file',
            'csv_lines',
            'operator',
        ]
        extra_kwargs = {
            'file': {'required': True}
        }

    def validate_file(self, value):
        """
        Validation du fichier uploadé:
        - Vérifie l'extension CSV
        - Vérifie que le fichier est lisible
        - Vérifie que toutes les colonnes attendues sont présentes
        """
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Le fichier doit avoir l'extension .csv.")

        try:
            df = pd.read_csv(value)
        except pd.errors.ParserError:
            raise serializers.ValidationError("Le fichier CSV est corrompu ou mal formé.")

        expected_columns = [
            'time', 'lat', 'lon', 'alt', 'gps_fix',
            'rat', 'mccmnc', 'cell_id',
            'pci',
            'band', 'earfcn',
            'rsrp_dbm', 'rsrq_db', 'sinr_db'
        ]

        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            raise serializers.ValidationError(
                f"Les colonnes suivantes sont manquantes dans le fichier CSV : {', '.join(missing_columns)}"
            )

        # On stocke le dataframe pour l'utiliser dans create/update
        self._csv_df = df
        return value

    def create(self, validated_data):
        """
        Création d'un GSMScan et des lignes CSV associées.
        Utilise une transaction atomique pour garantir l'intégrité des données.
        """
        operator = validated_data.pop('operator')
        gsm_data = GSMData.get(operator=operator)
        with transaction.atomic():
            file = validated_data.get('file')
            if file is None:
                raise serializers.ValidationError("Le fichier CSV est requis pour créer un GSMScan.")

            # Lecture du dataframe (déjà validé)
            df = getattr(self, '_csv_df', None)
            if df is None:
                df = pd.read_csv(file)

            # Création des lignes CSV
            csv_lines = []
            for _, row in df.iterrows():
                line = CSVLine.objects.create(**row.to_dict())
                csv_lines.append(line)

            # Enregistre le GSMScan avec la relation vers les lignes créées
            scan_instance = super().create(validated_data)
            scan_instance.csv_lines.set(csv_lines)
            gsm_data.gsm_scan.add(scan_instance)
            return scan_instance

    def update(self, instance, validated_data):
        """
        Mise à jour d'un GSMScan avec un nouveau fichier CSV.
        Les anciennes lignes sont supprimées et remplacées par les nouvelles.
        """
        with transaction.atomic():
            file = validated_data.get('file', None)
            if file:
                # Supprime les anciennes lignes pour éviter les doublons
                instance.cvs_line.all().delete()

                # Lecture du dataframe
                df = getattr(self, '_csv_df', None)
                if df is None:
                    df = pd.read_csv(file)

                # Création des nouvelles lignes CSV
                csv_lines = []
                for _, row in df.iterrows():
                    line = CSVLine.objects.create(**row.to_dict())
                    csv_lines.append(line)

                instance.cvs_line.set(csv_lines)

            return super().update(instance, validated_data)


class GSMDataSerializer(serializers.ModelSerializer):
    """
    Serializer pour GSMData.
    Les champs read_only assurent que seuls certains champs sont modifiables via l'API.
    """
    class Meta:
        model = GSMData
        fields = ['operator', 'gsm_scan']
        extra_kwargs = {
            'operator': {'required': True, 'read_only': True},
            'gsm_data': {'required': False, 'read_only': True},
        }
