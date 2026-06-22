{{- define "chroma.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "chroma.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "chroma.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "chroma.labels" -}}
app.kubernetes.io/name: {{ include "chroma.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}