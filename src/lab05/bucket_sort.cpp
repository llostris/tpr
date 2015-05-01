#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <omp.h>
#include <ctime>
#include <cstring>


using namespace std;

int parallelism_enabled = 0;
int num_threads = 1;

double parallel_section_time = 0.0;
double linear_section_time = 0.0;

void print_tab(float* tab, int n) {
  for ( int i = 0; i < n; i++ ) {
    cout << tab[i] << " ";
  }
  cout << "\n";
}

void bucketSort(float* tab, int n) {
  clock_t time_start, time_end;

  // distribute numbers to buckets

  time_start = clock();
  
  vector<float>* buckets = new vector<float>[n];
  int buckets_num = n / 100;
  if ( buckets_num == 0 ) {
    buckets_num = n;
  }

  for ( int i = 0; i < n; i++ ) {
    int bucket_nr = buckets_num * tab[i];
//    cout << bucket_nr << " " << tab[i] << "\n";
    buckets[bucket_nr].push_back(tab[i]);
  }

  time_end = clock();
  linear_section_time += (double) (time_end - time_start) / CLOCKS_PER_SEC;

  // sort buckets

  time_start = clock();

  int id;
  #pragma omp parallel for private(i, id) schedule(runtime) num_threads(num_threads)
  for ( int i = 0; i < buckets_num; i++ ) {
//    id = omp_get_thread_num();
//    printf("Iteracja %d wykonana przez watek nr. %d.\n", i, id);
    sort(buckets[i].begin(), buckets[i].end());
  }

  time_end = clock();
  parallel_section_time += (double) (time_end - time_start) / CLOCKS_PER_SEC;

  // concatenate buckets

  time_start = clock();

  int tab_index = 0;
  for ( int i = 0; i < buckets_num; i++ ) {
    for ( int j = 0; j < buckets[i].size(); j++ ) {
      tab[tab_index++] = buckets[i][j];
    }
  }
  time_end = clock();
  linear_section_time += (double) (time_end - time_start) / CLOCKS_PER_SEC;

  delete [] buckets;
}


int main(int argc, char** argv) {

  if ( argc < 4 ) {
    cout << "Invalid call. Usage: ./bucket_sort numbers_in_array number_of_threads [static|dynamic|guided] [chunk_size]\n";
    return -1;
  }

  int n = atoi(argv[1]);
  char* sched_type_name = argv[3];
  num_threads = atoi(argv[2]);

  int chunk = 0;  
  if ( argc == 5 ) {
    chunk = atoi(argv[4]);
  }
  cout << chunk << "\n";
  if ( strcmp(sched_type_name, "static") == 0 ) {
    omp_set_schedule(omp_sched_static, chunk); 
  } else if ( strcmp(sched_type_name, "dynamic") == 0 ) {
    omp_set_schedule(omp_sched_dynamic, chunk);
  } else if ( strcmp(sched_type_name, "guided") == 0 ) {
    omp_set_schedule(omp_sched_guided, chunk);
  }

  // generate tab
  float* tab = new float[n];
  for ( int i = 0; i < n; i++ ) {
    tab[i] = rand() / float(RAND_MAX);
  }

  // print_tab(tab, n);
  bucketSort(tab, n);
  // print_tab(tab, n);
  delete[] tab;
  printf("bucketsort1 %d %f %f\n", n, linear_section_time, parallel_section_time);

  return 0;
}

