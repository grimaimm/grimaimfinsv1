// document.addEventListener("DOMContentLoaded", function() {
//   var ctx = document.getElementById("chartjs-dashboard-line").getContext("2d");
//   var gradient = ctx.createLinearGradient(0, 0, 0, 225);
//   gradient.addColorStop(0, "rgba(255, 211, 105, 1)");
//   gradient.addColorStop(1, "rgba(255, 211, 105, 0)");
//   // Line chart
//   new Chart(document.getElementById("chartjs-dashboard-line"), {
//     type: "line",
//     data: {
//       labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
//       datasets: [{
//         label: "Sales ($)",
//         fill: true,
//         backgroundColor: gradient,
//         borderColor: "#222831",
//         data: [
//           2115,
//           1562,
//           1584,
//           1892,
//           1587,
//           1923,
//           2566,
//           2448,
//           2805,
//           3438,
//           2917,
//           3327
//         ]
//       }]
//     },
//     options: {
//       maintainAspectRatio: false,
//       legend: {
//         display: false
//       },
//       tooltips: {
//         intersect: false
//       },
//       hover: {
//         intersect: true
//       },
//       plugins: {
//         filler: {
//           propagate: false
//         }
//       },
//       scales: {
//         xAxes: [{
//           reverse: true,
//           gridLines: {
//             color: "rgba(0,0,0,0.0)"
//           }
//         }],
//         yAxes: [{
//           ticks: {
//             stepSize: 1000
//           },
//           display: true,
//           borderDash: [3, 3],
//           gridLines: {
//             color: "rgba(0,0,0,0.0)"
//           }
//         }]
//       }
//     }
//   });
// });


document.addEventListener("DOMContentLoaded", function() {
  var currentYear = new Date().getFullYear();

  // Fungsi untuk mengambil data bulanan dari server
  function fetchMonthlyData(year) {
      fetch(`/monthly_data_line/${year}`)
          .then(response => response.json())
          .then(monthlyData => {
              var ctx = document.getElementById("chartjs-dashboard-line").getContext("2d");
              var gradientPengeluaran = ctx.createLinearGradient(0, 0, 0, 225);
              gradientPengeluaran.addColorStop(0, "rgba(255, 211, 105, 1)");
              gradientPengeluaran.addColorStop(1, "rgba(255, 211, 105, 0)");

              var gradientPemasukan = ctx.createLinearGradient(0, 0, 0, 225);
              gradientPemasukan.addColorStop(0, "rgba(147, 127, 76, 1)");
              gradientPemasukan.addColorStop(1, "rgba(147, 127, 76, 0)");

              // Array untuk menyimpan nama bulan
              const monthNames = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
              ];

              // Line chart
              new Chart(ctx, {
                  type: "line",
                  data: {
                      labels: monthlyData.map(item => monthNames[item.month - 1]),
                      datasets: [{
                          label: "Pengeluaran",
                          fill: true,
                          backgroundColor: gradientPengeluaran,
                          borderColor: "rgba(255, 211, 105, 1)",
                          data: monthlyData.map(item => item.total_pengeluaran)
                      }, {
                          label: "Pemasukan",
                          fill: true,
                          backgroundColor: gradientPemasukan,
                          borderColor: "rgba(147, 127, 76, 1)",
                          data: monthlyData.map(item => item.total_pemasukan)
                      }]
                  },
                  options: {
                      maintainAspectRatio: false,
                      legend: {
                          display: true
                      },
                      tooltips: {
                          intersect: false,
                          callbacks: {
                              label: function(tooltipItem, data) {
                                  var label = data.datasets[tooltipItem.datasetIndex].label || '';

                                  if (label) {
                                      label += ': ';
                                  }

                                  // Format the currency with 'Rp.' and numeral formatting
                                  label += 'Rp. ' + numeral(tooltipItem.yLabel).format('0,0');

                                  return label;
                              }
                          }
                      },
                      hover: {
                          intersect: true
                      },
                      plugins: {
                          filler: {
                              propagate: false
                          }
                      },
                      scales: {
                          xAxes: [{
                              gridLines: {
                                  color: "rgba(0,0,0,0.1)"
                              }
                          }],
                          yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    return numeral(value/1000).format('0,0');
                                }
                            },
                            gridLines: {
                                display: true
                            }
                        }]
                      }
                  }
              });
          })
          .catch(error => console.error('Error fetching monthly data:', error));
  }

  // Panggil fungsi fetchMonthlyData dengan tahun saat ini
  fetchMonthlyData(currentYear);
});
