#include <iostream>
#include <cuda_runtime.h>
#include <stdio.h>
#include <bits/stdc++.h>

using namespace std;

// Number of variables (observations).  Equal to codeword length, n.
#define N_VARIABLES 10
// Number of edges to/from each variable (also the number of 1's in each col of H)
#define D_V 2

// Number of factors (parity checks).  Equal to parity length, k.
#define N_FACTORS 5
// Number of edges to/from each factor (also the number of 1's in each row of H)
#define D_C 4

// Channel Models (determines probability algorithm)
#define ALGO_SBC 1
#define ALGO_SEC 2
#define ALGO_AWGN 3

struct ldpc_info_t {
    bool valid;
    int iterations;
    int max_iterations;
};

__device__ void update_variable(int* f_indexes, int* v_indexes, float* msg_v_to_f, float* msg_f_to_v, float *observations, int v) {
    // update outgoing messages from a single variable to all factors
    if (v < N_VARIABLES) {
        // intitially sum = observation
        float sum = observations[v];
        // iteration 1: calculate sum over all contributing factors
        const int offset = v * D_V;
        for (int f=0; f < D_V; f++) {
            const int mi = v_indexes[offset + f];
            if (mi == -1) break;
            sum += msg_f_to_v[mi];
        }
        // iteration 2: subtract incoming contribution from outgoing edge
        for (int f=0; f < D_V; f++) {
            const int mi = v_indexes[offset + f];
            if (mi == -1) break;
            msg_v_to_f[v * D_V + f] = sum - msg_f_to_v[mi];
        }
    }
}

__device__ float arctanhf(float x) {
    return 0.5f * logf((1.0f + x) / (1.0f - x));
}

__device__ void update_factor(int* f_indexes, int* v_indexes, float* msg_v_to_f, float* msg_f_to_v, int f) {
    // update outgoing messages from a single factor to all variables
    if (f < N_FACTORS) {
        float L=1;
        
        // iteration 1: calculate L over all contributing variables
        const int offset = f * D_C;
        for (int v=0; v < D_C; v++) {
            const int mi = f_indexes[offset + v];
            if (mi == -1) break;
            L *= tanhf(msg_v_to_f[mi]/2.0f);
        }
        // iteration 2: divide (remove) incoming contribution from outgoing edge
        for (int v=0; v < D_C; v++) {
            const int mi = f_indexes[offset + v];
            if (mi == -1) break;
            msg_f_to_v[f*D_C + v] = 2.0f*arctanhf(L / tanhf(msg_v_to_f[mi]/2.0f));
        }
    }
}

__device__ void update_beliefs(int* f_indexes, int* v_indexes, float* msg_v_to_f, float* msg_f_to_v, float *observations, float *beliefs) {
    // like update_variable, but doesn't subtract any incoming messages
    for (int v = 0; v < N_VARIABLES; v++) {
        float sum = observations[v];

        // calculate sum over all contributing factors
        const int offset = v * D_V;
        for (int f=0; f < D_V; f++) {
            const int mi = v_indexes[offset + f];
            if (mi == -1) break;
            sum += msg_f_to_v[mi];
        }
        
        beliefs[v] = sum;
    }
}

__device__ bool valid_codeword(int* f_indexes, int* v_indexes, float *observations, float *beliefs) {
    
    for (int f=0; f < N_FACTORS; f++) {
        int parity_check = 0;
        const int offset = f * D_C;
        for (int v=0; v < D_C; v++) {
            int mi = f_indexes[offset + v];
            if (mi == -1) break;
            mi /= D_V;

            // observations are positive/negative for bit values of 0/1, respectively (yes, it seems backwards)
            // beliefs are negative/positive for disbelief/belief in the value of the observation
            //    ergo, beliefs multiplied by observations will simply invert the logic
            parity_check ^= (beliefs[mi] < 0) ? 1 : 0;
        }
        if (parity_check != 0) return false;

    }
    
    return true;
}

// CUDA kernel: add row index to each element in the row
__global__ void iterateLDPC(int* f_indexes, int* v_indexes, float* msg_v_to_f, float* msg_f_to_v, float *observations, float *beliefs, ldpc_info_t *ldpc_info) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    __shared__ bool codeword_is_valid;
    
    if (x >= N_VARIABLES) return;
    
    for (int i=0; i < ldpc_info->max_iterations; i++) {
        update_variable(f_indexes, v_indexes, msg_v_to_f, msg_f_to_v, observations, x);

        __syncthreads(); // sync required; factors require multiple variables

        update_factor(f_indexes, v_indexes, msg_v_to_f, msg_f_to_v, x);

        // Early iteration break check
        if (threadIdx.x == 0) {
            update_beliefs(f_indexes, v_indexes, msg_v_to_f, msg_f_to_v, observations, beliefs);
            codeword_is_valid = valid_codeword(f_indexes, v_indexes, observations, beliefs);
            ldpc_info->iterations = i + 1;
            ldpc_info->valid = codeword_is_valid;
        }

        __syncthreads();
        
        
        if (codeword_is_valid) {
            break;
        }
    }
}

void map_h_to_indexes(int *h_matrix, int *f_indexes, int *v_indexes) {
    // create mappings of edges from factors and variables, indexed into each other
    for (int f=0; f < N_FACTORS; f++) {
        int fi = 0;
        for (int v=0; v < N_VARIABLES; v++) {
            if (h_matrix[f * N_VARIABLES + v]) {

                int vi=0;
                while (v_indexes[(v * D_V + vi)] != -1) {
                    vi++;
                }
                v_indexes[(v * D_V + vi)] = f * D_C + fi;
                f_indexes[(f * D_C + fi)] = v * D_V + vi;

                fi++;
            }
        }
    }
}

int h_matrix[N_VARIABLES * N_FACTORS] =
    {1, 1, 1, 1, 0, 0, 0, 0, 0, 0,
     0, 1, 0, 0, 1, 0, 0, 0, 1, 1,
     1, 0, 1, 0, 0, 1, 1, 0, 0, 0,
     0, 0, 0, 1, 1, 0, 1, 1, 0, 0,
     0, 0, 0, 0, 0, 1, 0, 1, 1, 1};

                               // {1, 0, 1, 0, 1, 1, 1, 0, 1, 0}; // actual valid codeword
//float observations[N_VARIABLES] = {1, 1, 1, 0, 1, 1, 1, 0, 1, 0}; // hard erroneous codeword
float observations[N_VARIABLES] = {0.9, 0.1, 0.4, -0.7, 0.3, 0.8, 0.945, -0.6, 0.5, -0.76}; // soft erroneous codeword


int v_indexes[N_VARIABLES * D_V]; // variable indexes (that is, which factors are used to make a variable)
int f_indexes[N_FACTORS * D_C]; // factor indexes (that is, which variables are connected to a factor)

float messages_v_to_f[N_VARIABLES * D_V];
float messages_f_to_v[N_FACTORS * D_C];

float beliefs[N_VARIABLES];
int iterations = 10;


int main() {
    ldpc_info_t ldpc_info;
    ldpc_info.max_iterations = 10;

    cudaDeviceProp prop;
    int device = 0;
    cudaGetDeviceProperties(&prop, device);
    int maxThreadsPerBlock = prop.maxThreadsPerBlock;
    // Fallback for compute capability 6.1 (Pascal, e.g., GTX 1080): 1024 threads per block
    if (maxThreadsPerBlock <= 0) maxThreadsPerBlock = 1024;
    
    // Map the matrix to indexes
    memset(v_indexes, -1, sizeof(v_indexes));
    memset(f_indexes, -1, sizeof(f_indexes));
    map_h_to_indexes(h_matrix, f_indexes, v_indexes);
    
    // Output matrix and original observations
    std::cout << "Original matrix:\n";
    for (int f = 0; f < N_FACTORS; f++) {
        for (int v = 0; v < N_VARIABLES; ++v)
            std::cout << h_matrix[f*N_VARIABLES+v] << " ";
        std::cout << "\n";
    }
    std::cout << "\nObservations In:\n";
    for (int i = 0; i < N_VARIABLES; ++i) {
        std::cout << observations[i] << " ";
    }
    std::cout << "\n";

    // Update observations -> LLR
    for (int i=0; i < N_VARIABLES; ++i) {
        observations[i] = -2*observations[i];
    }
    
    // Allocate device memory
    int *cuda_f_indexes = NULL, *cuda_v_indexes = NULL;
    cudaMalloc(&cuda_f_indexes, N_FACTORS * D_C * sizeof(int));
    cudaMalloc(&cuda_v_indexes, N_VARIABLES * D_V * sizeof(int));

    float *cuda_observations = NULL, *cuda_beliefs = NULL;
    cudaMalloc(&cuda_observations, N_VARIABLES * sizeof(float));
    cudaMalloc(&cuda_beliefs, N_VARIABLES * sizeof(float)); // extra floats: [0] 0=invalid, 1=valid, [1] # iter
    
    ldpc_info_t *cuda_ldpc_info;
    cudaMalloc(&cuda_ldpc_info, sizeof(ldpc_info_t));

    float *cuda_messages_v_to_f = NULL, *cuda_messages_f_to_v = NULL;
    cudaMalloc(&cuda_messages_v_to_f, N_VARIABLES * D_V * sizeof(float));
    cudaMalloc(&cuda_messages_f_to_v, N_FACTORS * D_C * sizeof(float));

    // Copy matrix to device
    cudaMemcpy(cuda_f_indexes, f_indexes, N_FACTORS * D_C * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(cuda_v_indexes, v_indexes, N_VARIABLES * D_V * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(cuda_observations, observations, N_VARIABLES * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(cuda_ldpc_info, &ldpc_info, sizeof(ldpc_info_t), cudaMemcpyHostToDevice);

    // Launch kernel: one thread per row
    int threadsPerBlock = maxThreadsPerBlock;
    int blocksPerGrid = (N_VARIABLES + threadsPerBlock - 1) / threadsPerBlock;

    iterateLDPC<<<blocksPerGrid, threadsPerBlock>>>(cuda_f_indexes, cuda_v_indexes, cuda_messages_v_to_f, cuda_messages_f_to_v, cuda_observations, cuda_beliefs, cuda_ldpc_info);
    cudaDeviceSynchronize();

    // Copy result back to host
    cudaMemcpy(observations, cuda_observations, N_VARIABLES * sizeof(float), cudaMemcpyDeviceToHost);
    cudaMemcpy(beliefs, cuda_beliefs, N_VARIABLES * sizeof(float), cudaMemcpyDeviceToHost);
    cudaMemcpy(&ldpc_info, cuda_ldpc_info, sizeof(ldpc_info_t), cudaMemcpyDeviceToHost);

    printf("Valid = %d  Iterations Calculated = %d\n", ldpc_info.valid, ldpc_info.iterations);
    
    printf("  Original observations:   ");
    for (int v=0; v < N_VARIABLES; v++) {
        printf("%d", (observations[v] < 0) ? 1 : 0);
    }
    printf("\n");
    printf("  Final hard codeword found as: ");
    for (int v=0; v < N_VARIABLES; v++) {
        printf("%d", (beliefs[v] < 0) ? 1 : 0);
    }
    printf("\n");
    printf("  Final soft codeword found as: ");
    for (int v=0; v < N_VARIABLES; v++) {
        printf("%f ", beliefs[v] / -2);
    }
    printf("\n");
    printf("  Codeword stats: ");
    for (int v=0; v < N_VARIABLES; v++) {
        printf("%d (o=%f b=%f) ", (beliefs[v] < 0) ? 1 : 0, observations[v], beliefs[v]);
    }
    printf("\n");

    // Free CUDA memory
    cudaFree(cuda_f_indexes);
    cudaFree(cuda_v_indexes);
    cudaFree(cuda_observations);
    cudaFree(cuda_beliefs);
    cudaFree(cuda_ldpc_info);
    cudaFree(cuda_messages_v_to_f);
    cudaFree(cuda_messages_f_to_v);

    return 0;
}

