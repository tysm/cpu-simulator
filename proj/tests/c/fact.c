
int fact(int n)
{
    int ret = 1, i;
    for(i = 1; i <= n; ++i)
        ret *= i;
    return ret;
}

int main()
{
    return fact(5);
}
