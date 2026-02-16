from django.contrib import admin
from gsm_coverage.models import GSMData, GSMScan, CSVLine
from django.contrib.auth.models import Group

# --- Inline pour CSVLine dans GSMScan ---
class CSVLineInline(admin.TabularInline):
    model = GSMScan.csv_lines.through  # ManyToMany via table intermédiaire
    extra = 0
    verbose_name = "CSV Line"
    verbose_name_plural = "CSV Lines"

# --- Admin GSMScan ---
@admin.register(GSMScan)
class GSMScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'get_operators', 'created_at')
    search_fields = ('file',)
    list_filter = ('csv_lines__rat', 'csv_lines__mccmnc', 'csv_lines__band', 'created_at')
    date_hierarchy = 'created_at'
    inlines = [CSVLineInline]

    def get_operators(self, obj):
        # Retourne tous les opérateurs associés à ce scan
        return ", ".join([str(gsmdata.operator) for gsmdata in obj.gsmdata_set.all()])
    get_operators.short_description = "Operators"

# --- Admin CSVLine ---
class OperatorListFilter(admin.SimpleListFilter):
    title = 'operator'
    parameter_name = 'operator'

    def lookups(self, request, model_admin):
        # Retourne la liste des opérateurs
        operators = Group.objects.all()
        return [(op.id, op.name) for op in operators]

    def queryset(self, request, queryset):
        if self.value():
            # Filtre CSVLine via GSMScan -> GSMData -> operator
            return queryset.filter(
                gsmscan__gsmdata__operator__id=self.value()
            ).distinct()
        return queryset

@admin.register(CSVLine)
class CSVLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'lat', 'lon', 'alt', 'rat', 'mccmnc', 'cell_id', 'band', 'rsrp_dbm')
    search_fields = ('rat', 'mccmnc', 'cell_id')
    list_filter = (OperatorListFilter, 'rat', 'mccmnc', 'band', 'time')
    date_hierarchy = 'time'

# --- Admin GSMData ---
@admin.register(GSMData)
class GSMDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'operator', 'get_scans', 'created_at')
    search_fields = ('operator__name',)
    list_filter = ('operator', 'created_at')
    date_hierarchy = 'created_at'

    def get_scans(self, obj):
        return ", ".join([str(scan.file) for scan in obj.gsm_scan.all()])
    get_scans.short_description = "GSM Scans"
