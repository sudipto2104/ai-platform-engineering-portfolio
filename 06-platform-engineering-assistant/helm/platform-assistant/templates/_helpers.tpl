{{- define "platform-assistant.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "platform-assistant.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "platform-assistant.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "platform-assistant.labels" -}}
app.kubernetes.io/name: {{ include "platform-assistant.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}