
int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Usage: %s <filename>\n", argv[0]);
        return 1;
    }

    char *filename = argv[1];
    uint8_t *data;
    uint32_t num_items;
    uint32_t magic_number;

    FILE *fp = fopen(filename, "rb");
    if (!fp) {
        printf("Error opening file %s\n", filename);
        return 1;
    }

    // Print the IDX file header information
    print_idx_header_info(fp);

    // Read the magic number and number of items from the IDX file header
    fread(&magic_number, sizeof(magic_number), 1, fp);
    fread(&num_items, sizeof(num_items), 1, fp);
    magic_number = ntohl(magic_number);
    num_items = ntohl(num_items);

    uint32_t num_rows, num_cols;
    if (magic_number == 2051) {
        // Images file
        fread(&num_rows, sizeof(num_rows), 1, fp);
        fread(&num_cols, sizeof(num_cols), 1, fp);
        num_rows = ntohl(num_rows);
        num_cols = ntohl(num_cols);
        load_mnist_images(filename, &data, &num_items);
        flatten_images(data, num_items, num_rows, num_cols);
        free(data);
    } else if (magic_number == 2049) {
        // Labels file
        load_mnist_labels(filename, &data, &num_items);
        print_labels(data, num_items);
        free(data);
    } else {
        printf("Invalid IDX file format\n");
        return 1;
    }

    fclose(fp);
    return 0;
}
