function formatCurrency(input) {
  // Remove existing non-digit characters
  const value = input.value.replace(/[^0-9]/g, '');
  
  // Format the number with thousand separators
  const formattedValue = new Intl.NumberFormat('id-ID').format(value);
  
  // Update the input value with the formatted number
  input.value = `Rp. ${formattedValue}`;
}