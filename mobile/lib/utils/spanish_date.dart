/// Spanish date helpers kept dependency-free (no `intl`).
const List<String> _weekdays = [
  'lunes',
  'martes',
  'miércoles',
  'jueves',
  'viernes',
  'sábado',
  'domingo',
];

const List<String> _months = [
  'enero',
  'febrero',
  'marzo',
  'abril',
  'mayo',
  'junio',
  'julio',
  'agosto',
  'septiembre',
  'octubre',
  'noviembre',
  'diciembre',
];

/// e.g. `miércoles, 4 de noviembre`.
String longSpanishDate(DateTime date) {
  return '${_weekdays[date.weekday - 1]}, ${date.day} de ${_months[date.month - 1]}';
}

/// e.g. `04/11/2026`.
String shortDate(DateTime date) {
  final day = date.day.toString().padLeft(2, '0');
  final month = date.month.toString().padLeft(2, '0');
  return '$day/$month/${date.year}';
}
