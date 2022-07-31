float x = 12.34f;
write_to_file(reinterpret_cast<const std::byte *>(&x), sizeof(x)); // Ok